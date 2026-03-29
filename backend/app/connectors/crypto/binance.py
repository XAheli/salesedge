from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class BinanceConnector(BaseConnector):
    """Binance public market data connector.

    Uses the public (unauthenticated) endpoints for market data.
    Trading endpoints are out of scope for SalesEdge.
    """

    _IMPLEMENTED = True

    def __init__(
        self,
        api_key: str | None = None,
        api_secret: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="binance",
            base_url="https://api.binance.com/api/v3",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"api_key": api_key} if api_key else {},
            cache_manager=cache_manager,
            timeout=15.0,
        )

    async def get_ticker_price(self, symbol: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if symbol:
            params["symbol"] = symbol
        try:
            return await self._request(
                "GET",
                "/ticker/price",
                params=params,
                cache_key=f"binance:ticker:{symbol or 'all'}",
                cache_ttl=10,
            )
        except Exception as exc:
            logger.error("binance.get_ticker_price_failed", error=str(exc))
            raise

    async def get_klines(
        self, symbol: str, interval: str, limit: int = 100
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/klines",
                params={"symbol": symbol, "interval": interval, "limit": str(limit)},
                cache_key=f"binance:klines:{symbol}:{interval}:{limit}",
                cache_ttl=60,
            )
        except Exception as exc:
            logger.error("binance.get_klines_failed", error=str(exc))
            raise

    async def get_order_book(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/depth",
                params={"symbol": symbol, "limit": str(limit)},
                cache_key=f"binance:depth:{symbol}:{limit}",
                cache_ttl=5,
            )
        except Exception as exc:
            logger.error("binance.get_order_book_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/ping")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/ping"},
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
        return ["macro_context"]
