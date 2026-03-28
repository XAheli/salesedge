from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class UpstoxConnector(BaseConnector):
    """Upstox API connector — **stub, not yet fully implemented**.

    Authentication uses OAuth 2.0.  An ``access_token`` is required and
    must be refreshed via the Upstox login flow.
    """

    _IMPLEMENTED = False

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
        raise NotImplementedError("Upstox connector is not yet implemented")

    async def get_historical_data(
        self, instrument_key: str, interval: str, from_date: str, to_date: str
    ) -> dict[str, Any]:
        raise NotImplementedError("Upstox connector is not yet implemented")

    async def get_market_status(self) -> dict[str, Any]:
        raise NotImplementedError("Upstox connector is not yet implemented")

    async def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="degraded",
            last_check=datetime.now(timezone.utc),
            response_time_ms=0.0,
            error_rate=0.0,
            details={"reason": "stub — not yet implemented"},
        )

    def get_business_use_cases(self) -> list[str]:
        return ["deal_intelligence", "prospect_research"]
