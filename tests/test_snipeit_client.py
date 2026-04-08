"""Unit tests for SnipeITClient using respx to mock httpx."""

from __future__ import annotations

import pytest
import respx
from httpx import Response

from app.snipeit.client import AssetNotFound, SnipeITClient, UserNotFound

BASE = "https://snipeit.test"


@pytest.fixture
def client() -> SnipeITClient:
    return SnipeITClient(base_url=BASE, token="test-token", verify_ssl=False)


@pytest.mark.asyncio
@respx.mock
async def test_get_asset_by_tag_success(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/hardware/bytag/00042").mock(
        return_value=Response(
            200,
            json={
                "id": 42,
                "asset_tag": "00042",
                "name": "Dell Latitude",
                "serial": "SN-XYZ",
                "manufacturer": {"id": 1, "name": "Dell"},
                "model": {"id": 2, "name": "Latitude 5540"},
                "category": {"id": 3, "name": "Laptop"},
            },
        )
    )
    asset = await client.get_asset_by_tag("00042")
    assert asset.id == 42
    assert asset.asset_tag == "00042"
    assert asset.manufacturer_name == "Dell"


@pytest.mark.asyncio
@respx.mock
async def test_get_asset_by_tag_not_found(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/hardware/bytag/99999").mock(return_value=Response(404, json={}))
    with pytest.raises(AssetNotFound):
        await client.get_asset_by_tag("99999")


@pytest.mark.asyncio
@respx.mock
async def test_get_asset_by_tag_snipeit_error_body(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/hardware/bytag/00000").mock(
        return_value=Response(200, json={"status": "error", "messages": "Asset not found"})
    )
    with pytest.raises(AssetNotFound):
        await client.get_asset_by_tag("00000")


@pytest.mark.asyncio
@respx.mock
async def test_get_user_by_username_success(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/users").mock(
        return_value=Response(
            200,
            json={
                "total": 1,
                "rows": [{"id": 7, "username": "j.doe", "name": "John Doe"}],
            },
        )
    )
    user = await client.get_user_by_username("j.doe")
    assert user.id == 7
    assert user.display_name == "John Doe"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_by_username_not_found(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/users").mock(
        return_value=Response(200, json={"total": 0, "rows": []})
    )
    with pytest.raises(UserNotFound):
        await client.get_user_by_username("nobody")


@pytest.mark.asyncio
@respx.mock
async def test_get_last_checkout(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/reports/activity").mock(
        return_value=Response(
            200,
            json={
                "rows": [
                    {
                        "id": 100,
                        "action_type": "checkout",
                        "admin": {"id": 1, "name": "Admin User"},
                        "created_at": {"datetime": "2024-06-15T09:00:00.000000Z", "formatted": "2024-06-15 09:00"},
                    }
                ]
            },
        )
    )
    record = await client.get_last_checkout(42)
    assert record is not None
    assert record.admin_name == "Admin User"


@pytest.mark.asyncio
@respx.mock
async def test_get_last_checkout_none(client: SnipeITClient) -> None:
    respx.get(f"{BASE}/api/v1/reports/activity").mock(
        return_value=Response(200, json={"rows": []})
    )
    record = await client.get_last_checkout(42)
    assert record is None
