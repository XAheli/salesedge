from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_CATALOG = 3600  # 1 hour
CACHE_TTL_RESOURCE = 900  # 15 min


class OGDIndiaConnector(BaseConnector):
    """Open Government Data Platform India (data.gov.in) connector.

    Provides access to thousands of public datasets published by Indian
    ministries and departments.  Authentication is via an API key passed
    as the ``api-key`` query parameter.
    """

    def __init__(
        self,
        api_key: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="ogd_india",
            base_url="https://api.data.gov.in",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            auth_config={"api_key": api_key},
            cache_manager=cache_manager,
        )
        self._api_key = api_key

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        params["api-key"] = self._api_key

    # ── Public API ───────────────────────────────────────────────

    async def search_datasets(
        self,
        query: str,
        *,
        ministry: str | None = None,
        department: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search / list datasets on OGD India."""
        params: dict[str, Any] = {
            "format": "json",
            "limit": limit,
            "offset": offset,
        }
        if query:
            params["search"] = query
        if ministry:
            params["filters[org]"] = ministry
        if department:
            params["filters[department]"] = department

        cache_key = self._cache_key("search", params)
        return await self._request(
            "GET",
            "/lists",
            params=params,
            cache_key=cache_key,
            cache_ttl=CACHE_TTL_CATALOG,
        )

    async def get_resource(
        self,
        resource_id: str,
        *,
        fmt: str = "json",
        limit: int = 100,
        offset: int = 0,
        filters: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Fetch a specific dataset resource by its resource ID."""
        params: dict[str, Any] = {
            "format": fmt,
            "limit": limit,
            "offset": offset,
        }
        if filters:
            for k, v in filters.items():
                params[f"filters[{k}]"] = v

        cache_key = self._cache_key(f"resource:{resource_id}", params)
        return await self._request(
            "GET",
            f"/resource/{resource_id}",
            params=params,
            cache_key=cache_key,
            cache_ttl=CACHE_TTL_RESOURCE,
        )

    async def list_catalogs(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List available data catalogs."""
        params: dict[str, Any] = {
            "format": "json",
            "limit": limit,
            "offset": offset,
        }
        cache_key = self._cache_key("catalogs", params)
        return await self._request(
            "GET",
            "/catalogs",
            params=params,
            cache_key=cache_key,
            cache_ttl=CACHE_TTL_CATALOG,
        )

    async def discover_datasets_by_ministry(
        self,
        ministry_name: str,
        *,
        page_size: int = 100,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Paginated crawl of datasets published by a specific ministry."""
        all_records: list[dict[str, Any]] = []
        for page in range(max_pages):
            offset = page * page_size
            try:
                result = await self.search_datasets(
                    "", ministry=ministry_name, limit=page_size, offset=offset
                )
                records = result.get("records", [])
                all_records.extend(records)
                total = int(result.get("total", 0))
                if offset + page_size >= total:
                    break
            except Exception:
                logger.warning(
                    "ministry_discovery_page_failed",
                    ministry=ministry_name,
                    page=page,
                )
                break
        return all_records

    async def get_dataset_coverage_report(self) -> dict[str, Any]:
        """Build a coverage report summarising dataset counts by ministry/sector."""
        result = await self.search_datasets("", limit=1)
        total = int(result.get("total", 0))
        catalogs = await self.list_catalogs(limit=100)
        catalog_list = catalogs.get("records", [])
        return {
            "total_datasets": total,
            "catalog_count": len(catalog_list),
            "catalogs": catalog_list[:20],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def score_data_quality(self, resource_data: dict[str, Any]) -> dict[str, Any]:
        """Heuristic quality score for an OGD resource response."""
        records = resource_data.get("records", [])
        total = int(resource_data.get("total", 0))
        fields = resource_data.get("fields", [])

        record_count = len(records)
        completeness = 0.0
        if records and fields:
            field_names = [f.get("id", f.get("name", "")) for f in fields]
            non_null_counts = sum(
                1
                for r in records
                for fn in field_names
                if r.get(fn) not in (None, "", "NA", "N/A")
            )
            total_cells = record_count * len(field_names) if field_names else 1
            completeness = non_null_counts / total_cells

        return {
            "record_count": record_count,
            "total_available": total,
            "field_count": len(fields),
            "completeness": round(completeness, 3),
            "quality_tier": (
                "high" if completeness > 0.85
                else "medium" if completeness > 0.6
                else "low"
            ),
        }

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        import time

        start = time.monotonic()
        try:
            result = await self.search_datasets("health", limit=1)
            elapsed = (time.monotonic() - start) * 1000
            has_records = bool(result.get("records"))
            return ConnectorHealth(
                status="healthy" if has_records else "degraded",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"total_datasets": result.get("total", 0)},
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="unhealthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"error": str(exc)},
            )

    def get_business_use_cases(self) -> list[str]:
        return [
            "prospect_research",
            "macro_context",
            "industry_sizing",
            "territory_planning",
        ]

    # ── Internal helpers ─────────────────────────────────────────

    @staticmethod
    def _cache_key(prefix: str, params: dict[str, Any]) -> str:
        raw = f"ogd:{prefix}:{sorted(params.items())}"
        digest = hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]
        return f"ogd:{prefix}:{digest}"
