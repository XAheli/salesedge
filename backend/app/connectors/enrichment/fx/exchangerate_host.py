from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class ExchangeRateHostConnector(BaseConnector):
    """exchangerate.host FX connector.

    Provides a fallback FX rate source when Open Exchange Rates
    quota is exhausted.
    """

    _IMPLEMENTED = True

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
        params: dict[str, Any] = {"base": base}
        if symbols:
            params["symbols"] = symbols
        try:
            return await self._request(
                "GET",
                "/latest",
                params=params,
                cache_key=f"fxhost:latest:{base}:{symbols or 'all'}",
                cache_ttl=3600,
            )
        except Exception as exc:
            logger.error("exchangerate_host.get_latest_rates_failed", error=str(exc))
            raise

    async def get_historical(
        self, date: str, base: str = "USD"
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                f"/{date}",
                params={"base": base},
                cache_key=f"fxhost:hist:{date}:{base}",
                cache_ttl=86400,
            )
        except Exception as exc:
            logger.error("exchangerate_host.get_historical_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/latest", params={"base": "USD", "symbols": "EUR"})
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/latest"},
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
