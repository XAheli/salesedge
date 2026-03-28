from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_LATEST = 1800  # 30 min
CACHE_TTL_HISTORICAL = 86_400  # 24 h


class OpenExchangeRatesConnector(BaseConnector):
    """Open Exchange Rates connector.

    Auth via ``app_id`` query parameter.
    Free tier allows latest rates with USD base only.
    """

    def __init__(
        self,
        app_id: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="open_exchange_rates",
            base_url="https://openexchangerates.org/api",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            auth_config={"app_id": app_id},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._app_id = app_id

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        params["app_id"] = self._app_id

    # ── Public methods ───────────────────────────────────────────

    async def get_latest_rates(
        self,
        base: str = "USD",
        symbols: str | None = None,
    ) -> dict[str, Any]:
        """Latest exchange rates.

        Parameters
        ----------
        symbols:
            Comma-separated currency codes to filter (e.g. ``INR,EUR,GBP``).
        """
        params: dict[str, Any] = {"base": base}
        if symbols:
            params["symbols"] = symbols
        return await self._request(
            "GET",
            "/latest.json",
            params=params,
            cache_key=f"oxr:latest:{base}:{symbols}",
            cache_ttl=CACHE_TTL_LATEST,
        )

    async def get_historical(
        self,
        date: str,
        base: str = "USD",
        symbols: str | None = None,
    ) -> dict[str, Any]:
        """Historical rates for a specific date (``YYYY-MM-DD``)."""
        params: dict[str, Any] = {"base": base}
        if symbols:
            params["symbols"] = symbols
        return await self._request(
            "GET",
            f"/historical/{date}.json",
            params=params,
            cache_key=f"oxr:hist:{date}:{base}:{symbols}",
            cache_ttl=CACHE_TTL_HISTORICAL,
        )

    async def get_currencies(self) -> dict[str, Any]:
        """List of all supported currencies."""
        return await self._request(
            "GET",
            "/currencies.json",
            cache_key="oxr:currencies",
            cache_ttl=CACHE_TTL_HISTORICAL,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_latest_rates(symbols="INR")
            elapsed = (time.monotonic() - start) * 1000
            has_rates = bool(data.get("rates"))
            return ConnectorHealth(
                status="healthy" if has_rates else "degraded",
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
        return ["macro_context", "deal_intelligence"]
