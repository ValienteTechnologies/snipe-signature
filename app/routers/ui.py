"""UI routes — the admin-facing web interface."""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.demo_data import DEMO_USER, all_checkout, all_return
from app.dependencies import LabelsDep, SettingsDep, SnipeITDep
from app.documents.registry import available_templates as _available_templates
from app.snipeit.client import AssetNotFound, UserNotFound

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

router = APIRouter()
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


def _ctx(**kwargs) -> dict:
    return {"doc_templates": _available_templates(), **kwargs}


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, labels: LabelsDep, settings: SettingsDep) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        _ctx(labels=labels, rfid_enabled=settings.sato_printer_ip is not None),
    )


@router.get("/users/search")
async def user_search(
    q: Annotated[str, Query(min_length=2)],
    snipeit: SnipeITDep,
) -> JSONResponse:
    users = await snipeit.search_users(q)
    return JSONResponse([
        {
            "id": u.id,
            "username": u.username,
            "display_name": u.display_name,
            "department": u.department.name if u.department else None,
        }
        for u in users
    ])


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
        _ctx(
            labels=labels,
            checkout_enriched=enriched,
            return_enriched=None,
            user=user,
            lookup_type="asset",
            lookup_value=tag,
            error=error,
            rfid_enabled=settings.sato_printer_ip is not None,
        ),
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
        _ctx(
            labels=labels,
            checkout_enriched=checkout_enriched,
            return_enriched=return_enriched,
            user=user,
            lookup_type="user",
            lookup_value=username,
            error=error,
            rfid_enabled=settings.sato_printer_ip is not None,
        ),
    )


@router.get("/demo", response_class=HTMLResponse)
async def demo_preview(
    request: Request,
    labels: LabelsDep,
    settings: SettingsDep,
) -> HTMLResponse:
    if not settings.demo:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return templates.TemplateResponse(
        request,
        "preview.html",
        _ctx(
            labels=labels,
            checkout_enriched=all_checkout(),
            return_enriched=all_return(),
            user=DEMO_USER,
            lookup_type="user",
            lookup_value="demo.user",
            error=None,
            is_demo=True,
            rfid_enabled=settings.sato_printer_ip is not None,
        ),
    )
