from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class ICICIBreezeConnector(BaseConnector):
    """ICICI Direct Breeze API connector — **stub, not yet fully implemented**.

    Authentication uses ``api_key`` + ``api_secret`` with a session
    token from the ICICI Direct SSO flow.
    """

    _IMPLEMENTED = False

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        session_token: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="icici_breeze",
            base_url="https://api.icicidirect.com/breezeapi/api/v1",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"api_key": api_key, "api_secret": api_secret},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._session_token = session_token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        headers["X-SessionToken"] = self._session_token or ""
        headers["apikey"] = self.auth_config.get("api_key", "")
        headers.setdefault("Content-Type", "application/json")

    async def get_quote(self, stock_code: str, exchange: str = "NSE") -> dict[str, Any]:
        raise NotImplementedError("ICICI Breeze connector is not yet implemented")

    async def get_historical_data(
        self, stock_code: str, exchange: str, interval: str, from_date: str, to_date: str
    ) -> dict[str, Any]:
        raise NotImplementedError("ICICI Breeze connector is not yet implemented")

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
