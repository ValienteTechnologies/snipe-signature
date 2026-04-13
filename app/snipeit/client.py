"""Async Snipe-IT API client."""

from __future__ import annotations

import httpx

from app.snipeit.models import ActivityRecord, Asset, AssetWithActivity, User


class SnipeITError(Exception):
    """Generic Snipe-IT API error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AssetNotFound(SnipeITError):
    pass


class UserNotFound(SnipeITError):
    pass


class SnipeITClient:
    """Thin async wrapper around the Snipe-IT REST API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        verify_ssl: bool = True,
        cf_access_client_id: str | None = None,
        cf_access_client_secret: str | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        headers: dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if cf_access_client_id:
            headers["CF-Access-Client-Id"] = cf_access_client_id
        if cf_access_client_secret:
            headers["CF-Access-Client-Secret"] = cf_access_client_secret
        self._client = httpx.AsyncClient(
            base_url=self._base,
            headers=headers,
            verify=verify_ssl,
            timeout=30.0,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    async def get_asset_by_tag(self, tag: str) -> Asset:
        resp = await self._client.get(f"/api/v1/hardware/bytag/{tag}")
        if resp.status_code == 404:
            raise AssetNotFound(f"Asset with tag '{tag}' not found.", 404)
        self._raise_for_status(resp)
        data = resp.json()
        if data.get("status") == "error":
            raise AssetNotFound(data.get("messages", f"Asset '{tag}' not found."), 404)
        return Asset.model_validate(data)

    async def get_asset_by_id(self, asset_id: int) -> Asset:
        resp = await self._client.get(f"/api/v1/hardware/{asset_id}")
        if resp.status_code == 404:
            raise AssetNotFound(f"Asset {asset_id} not found.", 404)
        self._raise_for_status(resp)
        return Asset.model_validate(resp.json())

    async def get_user_assets(self, user_id: int) -> list[Asset]:
        resp = await self._client.get(f"/api/v1/users/{user_id}/assets")
        self._raise_for_status(resp)
        data = resp.json()
        rows = data.get("rows") or []
        return [Asset.model_validate(r) for r in rows]

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    async def search_users(self, query: str, limit: int = 10) -> list[User]:
        resp = await self._client.get("/api/v1/users", params={"search": query, "limit": limit})
        self._raise_for_status(resp)
        rows = resp.json().get("rows") or []
        return [User.model_validate(r) for r in rows]

    async def get_user_by_username(self, username: str) -> User:
        resp = await self._client.get("/api/v1/users", params={"username": username, "limit": 1})
        self._raise_for_status(resp)
        data = resp.json()
        rows = data.get("rows") or []
        if not rows:
            raise UserNotFound(f"User '{username}' not found.", 404)
        return User.model_validate(rows[0])

    async def get_user_by_id(self, user_id: int) -> User:
        resp = await self._client.get(f"/api/v1/users/{user_id}")
        if resp.status_code == 404:
            raise UserNotFound(f"User {user_id} not found.", 404)
        self._raise_for_status(resp)
        return User.model_validate(resp.json())

    # ------------------------------------------------------------------
    # Activity / history
    # ------------------------------------------------------------------

    async def get_last_checkout(self, asset_id: int) -> ActivityRecord | None:
        """Return the most recent checkout activity record for an asset."""
        resp = await self._client.get(
            "/api/v1/reports/activity",
            params={
                "action_type": "checkout",
                "item_id": asset_id,
                "item_type": "asset",
                "limit": 1,
                "sort": "created_at",
                "order": "desc",
            },
        )
        self._raise_for_status(resp)
        rows = resp.json().get("rows") or []
        return ActivityRecord.model_validate(rows[0]) if rows else None

    async def get_last_checkin_for_user(self, user_id: int) -> list[ActivityRecord]:
        """Return the most recent checkin activities where the user was the target."""
        resp = await self._client.get(
            "/api/v1/reports/activity",
            params={
                "action_type": "checkin from",
                "target_id": user_id,
                "target_type": "user",
                "limit": 50,
                "sort": "created_at",
                "order": "desc",
            },
        )
        self._raise_for_status(resp)
        rows = resp.json().get("rows") or []
        return [ActivityRecord.model_validate(r) for r in rows]

    # ------------------------------------------------------------------
    # Enrichment helpers
    # ------------------------------------------------------------------

    async def get_checkin_assets_for_user(self, user_id: int) -> list[AssetWithActivity]:
        """Return assets that were checked in FROM this user, enriched with the checkin record."""
        import asyncio

        records = await self.get_last_checkin_for_user(user_id)

        # Deduplicate by asset id, keeping the most recent checkin record per asset
        seen: dict[int, ActivityRecord] = {}
        for r in records:
            if r.item and r.item.id and r.item.type == "asset":
                if r.item.id not in seen:
                    seen[r.item.id] = r

        if not seen:
            return []

        async def _fetch(asset_id: int, record: ActivityRecord) -> AssetWithActivity | None:
            try:
                asset = await self.get_asset_by_id(asset_id)
            except SnipeITError:
                return None
            return AssetWithActivity(
                asset=asset,
                admin_name=record.admin_name,
                activity_date=record.created_at_datetime,
            )

        results = await asyncio.gather(*[_fetch(aid, rec) for aid, rec in seen.items()])
        return [r for r in results if r is not None]

    async def enrich_assets_with_checkout(self, assets: list[Asset]) -> list[AssetWithActivity]:
        """Fetch the last checkout record for each asset concurrently."""
        import asyncio

        async def _enrich(asset: Asset) -> AssetWithActivity:
            try:
                record = await self.get_last_checkout(asset.id)
            except SnipeITError:
                record = None
            return AssetWithActivity(
                asset=asset,
                admin_name=record.admin_name if record else "",
                activity_date=record.created_at_datetime if record else None,
            )

        return list(await asyncio.gather(*[_enrich(a) for a in assets]))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _raise_for_status(self, resp: httpx.Response) -> None:
        if resp.status_code >= 400:
            raise SnipeITError(
                f"Snipe-IT API error {resp.status_code}: {resp.text[:200]}",
                resp.status_code,
            )
