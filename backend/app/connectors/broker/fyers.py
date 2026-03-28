from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class FyersConnector(BaseConnector):
    """Fyers API v3 connector — **stub, not yet fully implemented**.

    Authentication requires ``app_id`` and a session-based access
    token obtained via the Fyers OAuth flow.
    """

    _IMPLEMENTED = False

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
        raise NotImplementedError("Fyers connector is not yet implemented")

    async def get_historical_data(
        self, symbol: str, resolution: str, from_epoch: int, to_epoch: int
    ) -> dict[str, Any]:
        raise NotImplementedError("Fyers connector is not yet implemented")

    async def get_market_depth(self, symbol: str) -> dict[str, Any]:
        raise NotImplementedError("Fyers connector is not yet implemented")

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
