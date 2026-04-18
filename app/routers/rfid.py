"""RFID label print endpoint — drives the embedded SATO printer directly."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import sato
from app.dependencies import SettingsDep, SnipeITDep
from app.snipeit.client import AssetNotFound

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rfid")


class RfidPrintRequest(BaseModel):
    tag: str


@router.post("/print")
async def rfid_print(body: RfidPrintRequest, settings: SettingsDep, snipeit: SnipeITDep) -> dict:
    if settings.sato_printer_ip is None:
        raise HTTPException(status_code=503, detail="RFID printer not configured")

    try:
        asset = await snipeit.get_asset_by_tag(body.tag)
    except AssetNotFound:
        raise HTTPException(status_code=404, detail=f"Asset '{body.tag}' not found in Snipe-IT")

    label = sato.LabelData(
        asset_id=str(asset.id),
        asset_tag=asset.asset_tag,
        manufacturer=asset.manufacturer_name or "Unknown",
        model=asset.model_name or "Unknown",
        qr_data=f"{settings.sato_qr_base}/{asset.id}",
        chip_data=str(asset.id),
    )

    try:
        printer_response = await sato.print_label(
            ip=settings.sato_printer_ip,
            port=settings.sato_printer_port,
            label=label,
        )
    except OSError as exc:
        logger.warning("SATO printer connection failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"Could not reach printer: {exc}")

    return {"ok": True, "tag": asset.asset_tag, "printer_response": printer_response or None}
