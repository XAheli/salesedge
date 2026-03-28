from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_PRICE = 120  # 2 min
CACHE_TTL_MARKET = 300  # 5 min
CACHE_TTL_TRENDING = 600  # 10 min


class CoinGeckoConnector(BaseConnector):
    """CoinGecko cryptocurrency data connector.

    Auth via ``x-cg-demo-api-key`` header (demo/free tier).
    """

    def __init__(
        self,
        api_key: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="coingecko",
            base_url="https://api.coingecko.com/api/v3",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"api_key": api_key} if api_key else {},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._api_key = api_key

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        if self._api_key:
            headers["x-cg-demo-api-key"] = self._api_key
        headers.setdefault("Accept", "application/json")

    # ── Public methods ───────────────────────────────────────────

    async def get_coin_price(
        self,
        ids: str | list[str],
        vs_currencies: str | list[str] = "usd",
    ) -> dict[str, Any]:
        """Simple price for one or more coins.

        Parameters
        ----------
        ids:
            Comma-separated string or list of CoinGecko coin IDs
            (e.g. ``bitcoin``, ``ethereum``).
        """
        if isinstance(ids, list):
            ids = ",".join(ids)
        if isinstance(vs_currencies, list):
            vs_currencies = ",".join(vs_currencies)

        return await self._request(
            "GET",
            "/simple/price",
            params={
                "ids": ids,
                "vs_currencies": vs_currencies,
                "include_24hr_change": "true",
                "include_market_cap": "true",
            },
            cache_key=f"cg:price:{ids}:{vs_currencies}",
            cache_ttl=CACHE_TTL_PRICE,
        )

    async def get_trending(self) -> dict[str, Any]:
        """Top trending coins on CoinGecko."""
        return await self._request(
            "GET",
            "/search/trending",
            cache_key="cg:trending",
            cache_ttl=CACHE_TTL_TRENDING,
        )

    async def get_market_data(
        self,
        *,
        vs_currency: str = "usd",
        order: str = "market_cap_desc",
        per_page: int = 50,
        page: int = 1,
    ) -> dict[str, Any]:
        """Market data for top coins."""
        params: dict[str, Any] = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": "false",
        }
        return await self._request(
            "GET",
            "/coins/markets",
            params=params,
            cache_key=f"cg:markets:{vs_currency}:{order}:{per_page}:{page}",
            cache_ttl=CACHE_TTL_MARKET,
        )

    async def get_coin_detail(self, coin_id: str) -> dict[str, Any]:
        """Detailed data for a single coin."""
        return await self._request(
            "GET",
            f"/coins/{coin_id}",
            params={"localization": "false", "tickers": "false"},
            cache_key=f"cg:coin:{coin_id}",
            cache_ttl=CACHE_TTL_MARKET,
        )

    async def get_global_data(self) -> dict[str, Any]:
        """Global cryptocurrency market stats."""
        return await self._request(
            "GET",
            "/global",
            cache_key="cg:global",
            cache_ttl=CACHE_TTL_MARKET,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_coin_price("bitcoin", "usd")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if "bitcoin" in data else "degraded",
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
            "prospect_research",
        ]
