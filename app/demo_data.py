"""Shared mock data used by the /demo preview and /forms/demo/* endpoints."""

from __future__ import annotations

from datetime import datetime

from app.snipeit.models import Asset, AssetWithActivity, NamedValue, User

_ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    ("DEMO-001", "ThinkPad X1 Carbon", "Lenovo",    "X1 Carbon Gen 11",   "Laptop",       "SN-LN-001", "2024-01-15"),
    ("DEMO-002", "MacBook Pro 14",     "Apple",     "MacBook Pro M3",      "Laptop",       "SN-AP-002", "2024-02-03"),
    ("DEMO-003", "Dell UltraSharp 27", "Dell",      "U2723DE",             "Monitor",      "SN-DL-003", "2024-02-10"),
    ("DEMO-004", "iPhone 15 Pro",      "Apple",     "iPhone 15 Pro",       "Mobile Phone", "SN-AP-004", "2024-03-01"),
    ("DEMO-005", "Magic Mouse",        "Apple",     "Magic Mouse 3",       "Peripheral",   "SN-AP-005", "2024-03-01"),
    ("DEMO-006", "Logitech MX Keys",  "Logitech",  "MX Keys S",           "Peripheral",   "SN-LG-006", "2024-03-05"),
    ("DEMO-007", "WD External SSD",   "WD",        "My Passport 2TB",     "Storage",      "SN-WD-007", "2024-03-10"),
    ("DEMO-008", "Cisco IP Phone",    "Cisco",     "8841",                "VoIP Phone",   "SN-CS-008", "2024-03-12"),
    ("DEMO-009", "USB-C Hub 10-in-1", "Anker",     "PowerExpand 10-in-1", "Peripheral",   "SN-AN-009", "2024-03-15"),
    ("DEMO-010", "Surface Pro 9",     "Microsoft", "Surface Pro 9",       "Laptop",       "SN-MS-010", "2024-04-01"),
    ("DEMO-011", "AirPods Pro 2",     "Apple",     "AirPods Pro 2nd Gen", "Audio",        "SN-AP-011", "2024-04-05"),
    ("DEMO-012", "Samsung T7 SSD",    "Samsung",   "Portable SSD T7",     "Storage",      "SN-SM-012", "2024-04-08"),
    ("DEMO-013", "Yealink Webcam",    "Yealink",   "UVC34",               "Camera",       "SN-YL-013", "2024-04-10"),
    ("DEMO-014", "LG UltraWide 34",  "LG",        "34WQ75C-B",           "Monitor",      "SN-LG-014", "2024-04-12"),
    ("DEMO-015", "Jabra Evolve2 85", "Jabra",     "Evolve2 85",          "Audio",        "SN-JB-015", "2024-04-15"),
]

DEMO_USER = User(
    id=9999,
    username="demo.user",
    first_name="Demo",
    last_name="User",
    department=NamedValue(id=1, name="IT Department"),
)

# id → AssetWithActivity, built once at import time
_ALL: dict[int, AssetWithActivity] = {}
for _i, (_tag, _name, _mfr, _model, _cat, _serial, _date) in enumerate(_ROWS, start=1):
    _asset = Asset(
        id=_i,
        asset_tag=_tag,
        name=_name,
        serial=_serial,
        manufacturer=NamedValue(name=_mfr),
        model=NamedValue(name=_model),
        category=NamedValue(name=_cat),
        assigned_to=NamedValue(id=9999, name="Demo User"),
        last_checkout=datetime.fromisoformat(_date),
    )
    _ALL[_i] = AssetWithActivity(
        asset=_asset,
        admin_name="Admin",
        activity_date=datetime.fromisoformat(_date),
    )


def all_checkout() -> list[AssetWithActivity]:
    return list(_ALL.values())


def all_return() -> list[AssetWithActivity]:
    return list(_ALL.values())[:5]


def filter_by_ids(ids: list[int]) -> list[AssetWithActivity]:
    return [_ALL[i] for i in ids if i in _ALL]
