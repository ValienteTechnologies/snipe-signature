"""Form generation endpoints — produce DOCX, PDF, or a ZIP of both."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Annotated, Literal

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from app.demo_data import DEMO_USER, filter_by_ids
from app.dependencies import LabelsDep, SettingsDep, SnipeITDep
from app.documents.checkout import build_checkout_docx
from app.documents.pdf import build_checkout_pdf, build_return_pdf
from app.documents.registry import DEFAULT_TEMPLATE, available_templates
from app.documents.return_form import build_return_docx
from app.snipeit.client import AssetNotFound, UserNotFound
from app.snipeit.models import AssetWithActivity, User

router = APIRouter(prefix="/forms")

FormatParam = Annotated[Literal["docx", "pdf"], Query(description="Output format")]
TemplateParam = Annotated[str, Query(description="Document template name")]


class FormRequest(BaseModel):
    asset_ids: list[int]
    user_id: int | None = None


def _cleanup(*paths: Path) -> None:
    for p in paths:
        with contextlib.suppress(OSError):
            p.unlink(missing_ok=True)



def _single_response(
    path: Path, media_type: str, filename: str, background: BackgroundTasks
) -> StreamingResponse:
    background.add_task(_cleanup, path)
    return StreamingResponse(
        open(path, "rb"),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _fetch_enriched(
    snipeit: SnipeITDep,
    body: FormRequest,
) -> tuple[list[AssetWithActivity], User]:
    """Fetch and enrich assets; resolve the user from body or asset assignment."""
    assets = []
    for asset_id in body.asset_ids:
        try:
            asset = await snipeit.get_asset_by_id(asset_id)
            assets.append(asset)
        except AssetNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not assets:
        raise HTTPException(status_code=400, detail="No valid assets provided.")

    enriched = await snipeit.enrich_assets_with_checkout(assets)

    # Resolve user
    user_id = body.user_id
    if user_id is None:
        # Fall back to the assigned user of the first asset
        first = assets[0]
        if first.assigned_to and first.assigned_to.id:
            user_id = first.assigned_to.id

    if user_id is None:
        raise HTTPException(status_code=422, detail="Could not determine user for this form.")

    try:
        user = await snipeit.get_user_by_id(user_id)
    except UserNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return enriched, user


@router.post("/checkout")
async def checkout_form(
    body: FormRequest,
    fmt: FormatParam = "pdf",
    template: TemplateParam = DEFAULT_TEMPLATE,
    snipeit: SnipeITDep = ...,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched, user = await _fetch_enriched(snipeit, body)
    logo = settings.logo_path
    footer = settings.doc_footer_text
    safe_name = (user.username or str(user.id)).replace(" ", "_")

    if fmt == "docx":
        path = build_checkout_docx(enriched, user, labels, logo, template, footer)
        return _single_response(path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"checkout_{safe_name}.docx", background)

    path = build_checkout_pdf(enriched, user, labels, logo, template, footer)
    return _single_response(path, "application/pdf", f"checkout_{safe_name}.pdf", background)


@router.post("/demo/checkout")
async def demo_checkout_form(
    body: FormRequest,
    fmt: FormatParam = "pdf",
    template: TemplateParam = DEFAULT_TEMPLATE,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched = filter_by_ids(body.asset_ids)
    if not enriched:
        raise HTTPException(status_code=400, detail="No valid demo assets provided.")
    logo = settings.logo_path
    footer = settings.doc_footer_text

    if fmt == "docx":
        path = build_checkout_docx(enriched, DEMO_USER, labels, logo, template, footer)
        return _single_response(path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "checkout_demo.docx", background)

    path = build_checkout_pdf(enriched, DEMO_USER, labels, logo, template, footer)
    return _single_response(path, "application/pdf", "checkout_demo.pdf", background)


@router.post("/demo/return")
async def demo_return_form(
    body: FormRequest,
    fmt: FormatParam = "pdf",
    template: TemplateParam = DEFAULT_TEMPLATE,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched = filter_by_ids(body.asset_ids)
    if not enriched:
        raise HTTPException(status_code=400, detail="No valid demo assets provided.")
    logo = settings.logo_path
    footer = settings.doc_footer_text

    if fmt == "docx":
        path = build_return_docx(enriched, DEMO_USER, labels, logo, template, footer)
        return _single_response(path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "return_demo.docx", background)

    path = build_return_pdf(enriched, DEMO_USER, labels, logo, template, footer)
    return _single_response(path, "application/pdf", "return_demo.pdf", background)


@router.post("/return")
async def return_form(
    body: FormRequest,
    fmt: FormatParam = "pdf",
    template: TemplateParam = DEFAULT_TEMPLATE,
    snipeit: SnipeITDep = ...,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched, user = await _fetch_enriched(snipeit, body)
    logo = settings.logo_path
    footer = settings.doc_footer_text
    safe_name = (user.username or str(user.id)).replace(" ", "_")

    if fmt == "docx":
        path = build_return_docx(enriched, user, labels, logo, template, footer)
        return _single_response(path, "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"return_{safe_name}.docx", background)

    path = build_return_pdf(enriched, user, labels, logo, template, footer)
    return _single_response(path, "application/pdf", f"return_{safe_name}.pdf", background)
