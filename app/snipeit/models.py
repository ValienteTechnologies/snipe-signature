"""Pydantic models for Snipe-IT API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _parse_snipeit_date(v: object) -> datetime | None:
    """Snipe-IT wraps dates as {datetime: '...', formatted: '...'} or bare ISO strings."""
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, dict):
        raw = v.get("datetime")
        if not raw:
            return None
        v = raw
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


class NamedValue(BaseModel):
    """A generic {id, name, type} object used throughout the Snipe-IT API."""

    model_config = {"extra": "ignore"}

    id: int | None = None
    name: str | None = None
    type: str | None = None  # e.g. "asset", "user" — present on item/target fields


class Asset(BaseModel):
    model_config = {"extra": "ignore"}

    id: int
    asset_tag: str
    name: str | None = None
    serial: str | None = None
    manufacturer: NamedValue | None = None
    model: NamedValue | None = None
    category: NamedValue | None = None
    assigned_to: NamedValue | None = None
    last_checkout: datetime | None = None
    status_label: NamedValue | None = None

    @field_validator("last_checkout", mode="before")
    @classmethod
    def _parse_last_checkout(cls, v: object) -> datetime | None:
        return _parse_snipeit_date(v)

    @property
    def manufacturer_name(self) -> str:
        return (self.manufacturer and self.manufacturer.name) or ""

    @property
    def model_name(self) -> str:
        return (self.model and self.model.name) or ""

    @property
    def category_name(self) -> str:
        return (self.category and self.category.name) or ""

    @property
    def serial_display(self) -> str:
        return self.serial or "-"


class User(BaseModel):
    model_config = {"extra": "ignore"}

    id: int
    username: str | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    department: NamedValue | None = None

    @property
    def display_name(self) -> str:
        if self.name:
            return self.name
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.username or str(self.id)


class ActivityRecord(BaseModel):
    """A single activity log entry from /api/v1/reports/activity."""

    model_config = {"extra": "ignore"}

    id: int
    action_type: str | None = None
    item: NamedValue | None = None
    target: NamedValue | None = None
    admin: NamedValue | None = None
    note: str | None = None
    created_at: datetime | None = Field(default=None)

    @field_validator("created_at", mode="before")
    @classmethod
    def _parse_created_at(cls, v: object) -> datetime | None:
        return _parse_snipeit_date(v)

    @property
    def admin_name(self) -> str:
        return (self.admin and self.admin.name) or ""

    @property
    def created_at_datetime(self) -> datetime | None:
        return self.created_at


class AssetWithActivity(BaseModel):
    """An asset enriched with its most recent checkout/checkin activity."""

    asset: Asset
    admin_name: str = ""
    activity_date: datetime | None = None
