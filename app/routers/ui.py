"""UI routes — the admin-facing web interface."""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import LabelsDep, SettingsDep, SnipeITDep
from app.documents.registry import available_templates
from app.snipeit.client import AssetNotFound, UserNotFound

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

router = APIRouter()
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))
templates.env.globals["doc_templates"] = available_templates()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, labels: LabelsDep) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {"labels": labels})


@router.get("/assets/{tag}/preview", response_class=HTMLResponse)
async def asset_preview(
    request: Request,
    tag: str,
    snipeit: SnipeITDep,
    labels: LabelsDep,
    settings: SettingsDep,
) -> HTMLResponse:
    error: str | None = None
    enriched = []
    user = None

    try:
        asset = await snipeit.get_asset_by_tag(tag)
        enriched = await snipeit.enrich_assets_with_checkout([asset])

        if asset.assigned_to and asset.assigned_to.id:
            with contextlib.suppress(Exception):
                user = await snipeit.get_user_by_id(asset.assigned_to.id)

    except AssetNotFound:
        error = labels.error_not_found
    except Exception:
        error = labels.error_generic

    return templates.TemplateResponse(
        request,
        "preview.html",
        {
            "labels": labels,
            "checkout_enriched": enriched,
            "return_enriched": None,
            "user": user,
            "lookup_type": "asset",
            "lookup_value": tag,
            "error": error,
        },
    )


@router.get("/users/{username}/preview", response_class=HTMLResponse)
async def user_preview(
    request: Request,
    username: str,
    snipeit: SnipeITDep,
    labels: LabelsDep,
    settings: SettingsDep,
) -> HTMLResponse:
    error: str | None = None
    checkout_enriched = []
    return_enriched = []
    user = None

    try:
        user = await snipeit.get_user_by_username(username)
        assets, return_enriched = await asyncio.gather(
            snipeit.get_user_assets(user.id),
            snipeit.get_checkin_assets_for_user(user.id),
        )
        if assets:
            checkout_enriched = await snipeit.enrich_assets_with_checkout(assets)

    except UserNotFound:
        error = labels.error_not_found
    except Exception:
        error = labels.error_generic

    return templates.TemplateResponse(
        request,
        "preview.html",
        {
            "labels": labels,
            "checkout_enriched": checkout_enriched,
            "return_enriched": return_enriched,
            "user": user,
            "lookup_type": "user",
            "lookup_value": username,
            "error": error,
        },
    )
