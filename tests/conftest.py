"""Shared test fixtures."""

from __future__ import annotations

from datetime import datetime

import pytest

from app.snipeit.models import Asset, AssetWithActivity, NamedValue, User


@pytest.fixture
def sample_user() -> User:
    return User(
        id=1,
        username="j.doe",
        first_name="John",
        last_name="Doe",
        department=NamedValue(id=10, name="IT"),
    )


@pytest.fixture
def sample_asset() -> Asset:
    return Asset(
        id=42,
        asset_tag="00042",
        name="Dell Latitude 5540",
        serial="SN-ABC123",
        manufacturer=NamedValue(id=1, name="Dell"),
        model=NamedValue(id=2, name="Latitude 5540"),
        category=NamedValue(id=3, name="Laptop"),
        assigned_to=NamedValue(id=1, name="John Doe"),
        last_checkout=datetime(2024, 6, 15, 9, 0),
    )


@pytest.fixture
def sample_enriched(sample_asset: Asset) -> AssetWithActivity:
    return AssetWithActivity(
        asset=sample_asset,
        admin_name="Admin User",
        activity_date=datetime(2024, 6, 15, 9, 0),
    )
