from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class ExchangeRateHostConnector(BaseConnector):
    """exchangerate.host FX connector — **stub, not yet fully implemented**.

    Provides a fallback FX rate source when Open Exchange Rates
    quota is exhausted.
    """

    _IMPLEMENTED = False

    def __init__(
        self,
        api_key: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="exchangerate_host",
            base_url="https://api.exchangerate.host",
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
            params["access_key"] = self._api_key

    async def get_latest_rates(
        self, base: str = "USD", symbols: str | None = None
    ) -> dict[str, Any]:
        raise NotImplementedError("exchangerate.host connector is not yet implemented")

    async def get_historical(
        self, date: str, base: str = "USD"
    ) -> dict[str, Any]:
        raise NotImplementedError("exchangerate.host connector is not yet implemented")

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
