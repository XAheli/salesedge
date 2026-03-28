from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_LIVE = 300  # 5 min
CACHE_TTL_FUNDAMENTALS = 86_400  # 24 h


class FMPConnector(BaseConnector):
    """Financial Modeling Prep (FMP) connector.

    Provides financial statements, ratios, and company profiles.
    Auth via ``apikey`` query parameter.
    """

    def __init__(
        self,
        api_key: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="fmp",
            base_url="https://financialmodelingprep.com/api/v3",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"api_key": api_key},
            cache_manager=cache_manager,
            timeout=20.0,
        )
        self._api_key = api_key

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        params["apikey"] = self._api_key

    # ── Public methods ───────────────────────────────────────────

    async def get_profile(self, symbol: str) -> dict[str, Any]:
        """Company profile."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            f"/profile/{symbol}",
            cache_key=f"fmp:profile:{symbol}",
            cache_ttl=CACHE_TTL_FUNDAMENTALS,
        )

    async def get_financial_statements(
        self,
        symbol: str,
        *,
        statement: str = "income-statement",
        period: str = "annual",
        limit: int = 5,
    ) -> dict[str, Any]:
        """Financial statements (income, balance-sheet, or cash-flow).

        Parameters
        ----------
        statement:
            ``income-statement``, ``balance-sheet-statement``,
            or ``cash-flow-statement``.
        period:
            ``annual`` or ``quarter``.
        """
        symbol = symbol.upper()
        return await self._request(
            "GET",
            f"/{statement}/{symbol}",
            params={"period": period, "limit": limit},
            cache_key=f"fmp:{statement}:{symbol}:{period}:{limit}",
            cache_ttl=CACHE_TTL_FUNDAMENTALS,
        )

    async def get_ratios(
        self, symbol: str, *, period: str = "annual", limit: int = 5
    ) -> dict[str, Any]:
        """Financial ratios (P/E, ROE, debt/equity, etc.)."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            f"/ratios/{symbol}",
            params={"period": period, "limit": limit},
            cache_key=f"fmp:ratios:{symbol}:{period}:{limit}",
            cache_ttl=CACHE_TTL_FUNDAMENTALS,
        )

    async def get_key_metrics(
        self, symbol: str, *, period: str = "annual", limit: int = 5
    ) -> dict[str, Any]:
        """Key financial metrics."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            f"/key-metrics/{symbol}",
            params={"period": period, "limit": limit},
            cache_key=f"fmp:metrics:{symbol}:{period}:{limit}",
            cache_ttl=CACHE_TTL_FUNDAMENTALS,
        )

    async def get_stock_screener(
        self,
        *,
        market_cap_more_than: int | None = None,
        sector: str | None = None,
        country: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Stock screener with filters."""
        params: dict[str, Any] = {"limit": limit}
        if market_cap_more_than is not None:
            params["marketCapMoreThan"] = market_cap_more_than
        if sector:
            params["sector"] = sector
        if country:
            params["country"] = country
        return await self._request(
            "GET",
            "/stock-screener",
            params=params,
            cache_key=f"fmp:screener:{market_cap_more_than}:{sector}:{country}:{limit}",
            cache_ttl=CACHE_TTL_LIVE,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_profile("AAPL")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if data else "degraded",
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
            "prospect_research",
            "competitive_intelligence",
            "deal_intelligence",
        ]
