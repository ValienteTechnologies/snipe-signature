"""Form generation endpoints — produce PDF receipts."""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from app.demo_data import DEMO_USER, filter_by_ids
from app.dependencies import LabelsDep, SettingsDep, SnipeITDep
from app.documents.pdf import build_checkout_pdf, build_return_pdf
from app.documents.registry import DEFAULT_TEMPLATE, available_templates
from app.snipeit.client import AssetNotFound, UserNotFound
from app.snipeit.models import AssetWithActivity, User

router = APIRouter(prefix="/forms")

TemplateParam = Annotated[str, Query(description="Document template name")]


class FormRequest(BaseModel):
    asset_ids: list[int]
    user_id: int | None = None


def _cleanup(*paths: Path) -> None:
    for p in paths:
        with contextlib.suppress(OSError):
            p.unlink(missing_ok=True)


def _single_response(
    path: Path, filename: str, background: BackgroundTasks
) -> StreamingResponse:
    background.add_task(_cleanup, path)
    return StreamingResponse(
        open(path, "rb"),
        media_type="application/pdf",
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
    template: TemplateParam = DEFAULT_TEMPLATE,
    snipeit: SnipeITDep = ...,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched, user = await _fetch_enriched(snipeit, body)
    safe_name = (user.username or str(user.id)).replace(" ", "_")
    path = build_checkout_pdf(enriched, user, labels, settings.logo_path, template, settings.doc_footer_text)
    return _single_response(path, f"checkout_{safe_name}.pdf", background)


@router.post("/demo/checkout")
async def demo_checkout_form(
    body: FormRequest,
    template: TemplateParam = DEFAULT_TEMPLATE,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    if not settings.demo:
        raise HTTPException(status_code=404)
    enriched = filter_by_ids(body.asset_ids)
    if not enriched:
        raise HTTPException(status_code=400, detail="No valid demo assets provided.")
    path = build_checkout_pdf(enriched, DEMO_USER, labels, settings.logo_path, template, settings.doc_footer_text)
    return _single_response(path, "checkout_demo.pdf", background)


@router.post("/demo/return")
async def demo_return_form(
    body: FormRequest,
    template: TemplateParam = DEFAULT_TEMPLATE,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    if not settings.demo:
        raise HTTPException(status_code=404)
    enriched = filter_by_ids(body.asset_ids)
    if not enriched:
        raise HTTPException(status_code=400, detail="No valid demo assets provided.")
    path = build_return_pdf(enriched, DEMO_USER, labels, settings.logo_path, template, settings.doc_footer_text)
    return _single_response(path, "return_demo.pdf", background)


@router.post("/return")
async def return_form(
    body: FormRequest,
    template: TemplateParam = DEFAULT_TEMPLATE,
    snipeit: SnipeITDep = ...,
    labels: LabelsDep = ...,
    settings: SettingsDep = ...,
    background: BackgroundTasks = ...,
) -> Response:
    enriched, user = await _fetch_enriched(snipeit, body)
    safe_name = (user.username or str(user.id)).replace(" ", "_")
    path = build_return_pdf(enriched, user, labels, settings.logo_path, template, settings.doc_footer_text)
    return _single_response(path, f"return_{safe_name}.pdf", background)
