from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class UpstoxConnector(BaseConnector):
    """Upstox API connector.

    Authentication uses OAuth 2.0.  An ``access_token`` is required and
    must be refreshed via the Upstox login flow.
    """

    _IMPLEMENTED = True

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="upstox",
            base_url="https://api.upstox.com/v2",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"api_key": api_key, "api_secret": api_secret},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._access_token = access_token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        headers.setdefault("Accept", "application/json")

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/market-quote/quotes",
                params={"instrument_key": symbol},
                cache_key=f"upstox:quote:{symbol}",
                cache_ttl=10,
            )
        except Exception as exc:
            logger.error("upstox.get_quote_failed", error=str(exc))
            raise

    async def get_historical_data(
        self, instrument_key: str, interval: str, from_date: str, to_date: str
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                f"/historical-candle/{instrument_key}/{interval}/{to_date}/{from_date}",
                cache_key=f"upstox:hist:{instrument_key}:{interval}:{from_date}:{to_date}",
                cache_ttl=300,
            )
        except Exception as exc:
            logger.error("upstox.get_historical_data_failed", error=str(exc))
            raise

    async def get_market_status(self) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/market/status/exchange",
                cache_key="upstox:market_status",
                cache_ttl=60,
            )
        except Exception as exc:
            logger.error("upstox.get_market_status_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/market/status/exchange")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/market/status/exchange"},
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
        return ["deal_intelligence", "prospect_research"]
