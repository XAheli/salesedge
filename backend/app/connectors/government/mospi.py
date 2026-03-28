from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL = 21_600  # 6 hours


class MOSPIConnector(BaseConnector):
    """MOSPI eSankhyiki connector for national statistical indicators.

    Provides GDP, CPI, IIP, trade statistics, employment data, and
    state-wise GSDP from the Ministry of Statistics & Programme
    Implementation's API.
    """

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="mospi",
            base_url="https://esankhyiki.mospi.gov.in/api/v1",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            cache_manager=cache_manager,
            timeout=40.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def get_gdp_data(
        self,
        *,
        frequency: str = "quarterly",
        series: str = "current",
    ) -> dict[str, Any]:
        """Fetch GDP data at the given frequency."""
        params: dict[str, Any] = {
            "indicator": "GDP",
            "frequency": frequency,
            "series": series,
        }
        return await self._request(
            "GET",
            "/data/gdp",
            params=params,
            cache_key=self._ck("gdp", params),
            cache_ttl=CACHE_TTL,
        )

    async def get_cpi_components(
        self, *, base_year: str = "2012"
    ) -> dict[str, Any]:
        """CPI components broken down by group."""
        params: dict[str, Any] = {"base_year": base_year}
        return await self._request(
            "GET",
            "/data/cpi",
            params=params,
            cache_key=self._ck("cpi", params),
            cache_ttl=CACHE_TTL,
        )

    async def get_iip_data(self) -> dict[str, Any]:
        """Index of Industrial Production."""
        return await self._request(
            "GET",
            "/data/iip",
            cache_key="mospi:iip",
            cache_ttl=CACHE_TTL,
        )

    async def get_trade_statistics(
        self,
        *,
        trade_type: str | None = None,
    ) -> dict[str, Any]:
        """Merchandise trade statistics (exports/imports)."""
        params: dict[str, Any] = {}
        if trade_type:
            params["type"] = trade_type
        return await self._request(
            "GET",
            "/data/trade",
            params=params,
            cache_key=self._ck("trade", params),
            cache_ttl=CACHE_TTL,
        )

    async def get_employment_data(self) -> dict[str, Any]:
        """Employment and labour-force statistics."""
        return await self._request(
            "GET",
            "/data/employment",
            cache_key="mospi:employment",
            cache_ttl=CACHE_TTL,
        )

    async def get_gsdp_data(
        self, *, state: str | None = None
    ) -> dict[str, Any]:
        """Gross State Domestic Product data."""
        params: dict[str, Any] = {}
        if state:
            params["state"] = state
        return await self._request(
            "GET",
            "/data/gsdp",
            params=params,
            cache_key=self._ck("gsdp", params),
            cache_ttl=CACHE_TTL,
        )

    async def search_indicators(self, query: str) -> dict[str, Any]:
        """Free-text search across MOSPI indicators."""
        params: dict[str, Any] = {"q": query}
        return await self._request(
            "GET",
            "/search",
            params=params,
            cache_key=self._ck("search", params),
            cache_ttl=CACHE_TTL,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/status", cache_key=None)
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
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
            "macro_context",
            "industry_sizing",
            "territory_planning",
        ]

    # ── Internal helpers ─────────────────────────────────────────

    @staticmethod
    def _ck(prefix: str, params: dict[str, Any]) -> str:
        raw = f"mospi:{prefix}:{sorted(params.items())}"
        digest = hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]
        return f"mospi:{prefix}:{digest}"
