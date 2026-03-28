from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_QUOTE = 120  # 2 min
CACHE_TTL_PROFILE = 86_400  # 24 h
CACHE_TTL_NEWS = 900  # 15 min


class FinnhubConnector(BaseConnector):
    """Finnhub stock-market data connector.

    Free tier: **60 requests/minute**.
    Auth via ``token`` query parameter.
    """

    def __init__(
        self,
        api_key: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="finnhub",
            base_url="https://finnhub.io/api/v1",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"api_key": api_key},
            rate_limit=60,
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._api_key = api_key

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        params["token"] = self._api_key

    # ── Public methods ───────────────────────────────────────────

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Real-time quote (c, h, l, o, pc, t)."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/quote",
            params={"symbol": symbol},
            cache_key=f"finnhub:quote:{symbol}",
            cache_ttl=CACHE_TTL_QUOTE,
        )

    async def get_company_profile(self, symbol: str) -> dict[str, Any]:
        """Company profile (name, industry, market cap, etc.)."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/stock/profile2",
            params={"symbol": symbol},
            cache_key=f"finnhub:profile:{symbol}",
            cache_ttl=CACHE_TTL_PROFILE,
        )

    async def get_company_news(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
    ) -> dict[str, Any]:
        """Company-specific news articles between two dates (``YYYY-MM-DD``)."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/company-news",
            params={"symbol": symbol, "from": from_date, "to": to_date},
            cache_key=f"finnhub:news:{symbol}:{from_date}:{to_date}",
            cache_ttl=CACHE_TTL_NEWS,
        )

    async def search_symbol(self, query: str) -> dict[str, Any]:
        """Search for a ticker symbol by name or partial symbol."""
        return await self._request(
            "GET",
            "/search",
            params={"q": query},
            cache_key=f"finnhub:search:{query.lower()}",
            cache_ttl=3600,
        )

    async def get_market_news(
        self, category: str = "general"
    ) -> dict[str, Any]:
        """General or category-specific market news."""
        return await self._request(
            "GET",
            "/news",
            params={"category": category},
            cache_key=f"finnhub:mkt_news:{category}",
            cache_ttl=CACHE_TTL_NEWS,
        )

    async def get_peers(self, symbol: str) -> dict[str, Any]:
        """Company peers / similar companies."""
        symbol = symbol.upper()
        return await self._request(
            "GET",
            "/stock/peers",
            params={"symbol": symbol},
            cache_key=f"finnhub:peers:{symbol}",
            cache_ttl=CACHE_TTL_PROFILE,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_quote("AAPL")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if data.get("c") else "degraded",
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
