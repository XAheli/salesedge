from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_QUOTE = 300  # 5 min
CACHE_TTL_OVERVIEW = 86_400  # 24 h
CACHE_TTL_SERIES = 3600  # 1 h


class AlphaVantageConnector(BaseConnector):
    """Alpha Vantage connector.

    Free tier: **25 requests/day** — use caching aggressively.
    Auth via ``apikey`` query parameter.
    """

    def __init__(
        self,
        api_key: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="alpha_vantage",
            base_url="https://www.alphavantage.co",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"api_key": api_key},
            rate_limit=25,
            cache_manager=cache_manager,
            timeout=20.0,
        )
        self._api_key = api_key

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        params["apikey"] = self._api_key

    # ── Public methods ───────────────────────────────────────────

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Global quote for a symbol."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/query",
            params={"function": "GLOBAL_QUOTE", "symbol": symbol},
            cache_key=f"av:quote:{symbol}",
            cache_ttl=CACHE_TTL_QUOTE,
        )

    async def get_time_series(
        self,
        symbol: str,
        *,
        function: str = "TIME_SERIES_DAILY",
        interval: str | None = None,
        outputsize: str = "compact",
    ) -> dict[str, Any]:
        """Time-series data (daily, weekly, monthly, or intraday).

        For intraday use ``function='TIME_SERIES_INTRADAY'`` with
        ``interval`` set to ``1min``, ``5min``, ``15min``, ``30min``,
        or ``60min``.
        """
        symbol = symbol.upper()
        params: dict[str, Any] = {
            "function": function,
            "symbol": symbol,
            "outputsize": outputsize,
        }
        if interval:
            params["interval"] = interval
        return await self._request(
            "GET",
            "/query",
            params=params,
            cache_key=f"av:ts:{symbol}:{function}:{interval}:{outputsize}",
            cache_ttl=CACHE_TTL_SERIES,
        )

    async def get_company_overview(self, symbol: str) -> dict[str, Any]:
        """Fundamental data / company overview."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/query",
            params={"function": "OVERVIEW", "symbol": symbol},
            cache_key=f"av:overview:{symbol}",
            cache_ttl=CACHE_TTL_OVERVIEW,
        )

    async def get_earnings(self, symbol: str) -> dict[str, Any]:
        """Annual and quarterly earnings."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/query",
            params={"function": "EARNINGS", "symbol": symbol},
            cache_key=f"av:earnings:{symbol}",
            cache_ttl=CACHE_TTL_OVERVIEW,
        )

    async def get_income_statement(self, symbol: str) -> dict[str, Any]:
        """Income statement data."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/query",
            params={"function": "INCOME_STATEMENT", "symbol": symbol},
            cache_key=f"av:income:{symbol}",
            cache_ttl=CACHE_TTL_OVERVIEW,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_quote("IBM")
            elapsed = (time.monotonic() - start) * 1000
            has_data = bool(data.get("Global Quote"))
            return ConnectorHealth(
                status="healthy" if has_data else "degraded",
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
            "macro_context",
        ]
