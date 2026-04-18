"""SATO RFID label printer — SBPL protocol over raw TCP socket."""

from __future__ import annotations

import asyncio
import logging
import socket
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LabelData:
    asset_id: str
    asset_tag: str
    manufacturer: str
    model: str
    qr_data: str
    chip_data: str


def _safe_text(value: object, max_length: int = 28) -> str:
    text = str(value or "").replace("\x1b", " ").replace("\n", " ").replace("\r", " ")
    return text[:max_length]


def _build_epc(chip_data: object) -> str:
    candidate = str(chip_data or "").strip()
    if candidate.isdigit():
        return candidate.zfill(24)
    hex_data = candidate.encode("utf-8").hex().upper()
    return hex_data[:24] if len(hex_data) > 24 else hex_data.zfill(24)


def _build_sbpl(label: LabelData) -> bytes:
    esc = "\x1b"
    qr_text = _safe_text(label.qr_data, max_length=64)
    qr_len = len(qr_text.encode("utf-8"))
    epc = _build_epc(label.chip_data)

    command = (
        f"{esc}A"
        f"{esc}V0010{esc}H0320{esc}XMID: {_safe_text(label.asset_id)}"
        f"{esc}V0040{esc}H0320{esc}XMTag: {_safe_text(label.asset_tag)}"
        f"{esc}V0070{esc}H0320{esc}XMManufacturer: {_safe_text(label.manufacturer)}"
        f"{esc}V0100{esc}H0320{esc}XMModel: {_safe_text(label.model)}"
        f"{esc}V0005{esc}H0190{esc}2D30,M,03,1,0"
        f"{esc}DN{qr_len:04d},{qr_text}"
        f"{esc}IP0e:h,epc:{epc},fsw:1;"
        f"{esc}Q1"
        f"{esc}Z"
    )
    return command.encode("utf-8")


def _send_sync(ip: str, port: int, payload: bytes, timeout: float) -> str:
    """Send SBPL payload and return any printer response (empty string if none)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        s.connect((ip, port))
        s.sendall(payload)
        try:
            response = s.recv(2048)
            return response.decode("ascii", errors="replace").strip()
        except TimeoutError:
            return ""


async def print_label(
    *,
    ip: str,
    port: int,
    label: LabelData,
    timeout: float = 5.0,
) -> str:
    """Send a label print job to the SATO printer over raw TCP.

    Returns the raw printer response string (may be empty).
    Raises OSError on connection or send failure.
    """
    payload = _build_sbpl(label)
    logger.debug("Sending %d bytes to SATO printer %s:%d (tag=%r)", len(payload), ip, port, label.asset_tag)
    response = await asyncio.to_thread(_send_sync, ip, port, payload, timeout)
    logger.info("SATO printer %s:%d response for tag=%r: %r", ip, port, label.asset_tag, response or "<none>")
    return response
