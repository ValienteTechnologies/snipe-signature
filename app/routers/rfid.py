"""RFID printer proxy endpoint."""

from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.dependencies import SettingsDep

router = APIRouter(prefix="/rfid")


class RfidPrintRequest(BaseModel):
    tag: str


@router.post("/print")
async def rfid_print(body: RfidPrintRequest, settings: SettingsDep) -> dict:
    if settings.rfid_printer_url is None:
        raise HTTPException(status_code=503, detail="RFID printer not configured")

    url = str(settings.rfid_printer_url)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(url, json={"tag": body.tag})
            resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"Printer returned {exc.response.status_code}") from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach printer: {exc}") from exc

    try:
        return resp.json()
    except Exception:
        return {"ok": True}
