from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class BinanceConnector(BaseConnector):
    """Binance public market data connector — **stub, not yet fully implemented**.

    Uses the public (unauthenticated) endpoints for market data.
    Trading endpoints are out of scope for SalesEdge.
    """

    _IMPLEMENTED = False

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
        raise NotImplementedError("Binance connector is not yet implemented")

    async def get_klines(
        self, symbol: str, interval: str, limit: int = 100
    ) -> dict[str, Any]:
        raise NotImplementedError("Binance connector is not yet implemented")

    async def get_order_book(self, symbol: str, limit: int = 20) -> dict[str, Any]:
        raise NotImplementedError("Binance connector is not yet implemented")

    async def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="degraded",
            last_check=datetime.now(timezone.utc),
            response_time_ms=0.0,
            error_rate=0.0,
            details={"reason": "stub — not yet implemented"},
        )

    def get_business_use_cases(self) -> list[str]:
        return ["macro_context"]
