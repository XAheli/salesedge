from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class FyersConnector(BaseConnector):
    """Fyers API v3 connector.

    Authentication requires ``app_id`` and a session-based access
    token obtained via the Fyers OAuth flow.
    """

    _IMPLEMENTED = True

    def __init__(
        self,
        app_id: str,
        secret_key: str,
        access_token: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="fyers",
            base_url="https://api-t1.fyers.in/api/v3",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"app_id": app_id, "secret_key": secret_key},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._access_token = access_token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        if self._access_token:
            headers["Authorization"] = f"{self.auth_config['app_id']}:{self._access_token}"
        headers.setdefault("Content-Type", "application/json")

    async def get_quote(self, symbols: list[str]) -> dict[str, Any]:
        symbols_str = ",".join(symbols)
        try:
            return await self._request(
                "GET",
                "/quotes/",
                params={"symbols": symbols_str},
                cache_key=f"fyers:quote:{symbols_str}",
                cache_ttl=10,
            )
        except Exception as exc:
            logger.error("fyers.get_quote_failed", error=str(exc))
            raise

    async def get_historical_data(
        self, symbol: str, resolution: str, from_epoch: int, to_epoch: int
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/history/",
                params={
                    "symbol": symbol,
                    "resolution": resolution,
                    "date_format": "0",
                    "range_from": str(from_epoch),
                    "range_to": str(to_epoch),
                    "cont_flag": "1",
                },
                cache_key=f"fyers:hist:{symbol}:{resolution}:{from_epoch}:{to_epoch}",
                cache_ttl=300,
            )
        except Exception as exc:
            logger.error("fyers.get_historical_data_failed", error=str(exc))
            raise

    async def get_market_depth(self, symbol: str) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/depth/",
                params={"symbol": symbol, "ohlcv_flag": "1"},
                cache_key=f"fyers:depth:{symbol}",
                cache_ttl=5,
            )
        except Exception as exc:
            logger.error("fyers.get_market_depth_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/quotes/", params={"symbols": "NSE:NIFTY50-INDEX"})
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/quotes/"},
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
