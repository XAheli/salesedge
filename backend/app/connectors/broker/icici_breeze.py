from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class ICICIBreezeConnector(BaseConnector):
    """ICICI Direct Breeze API connector.

    Authentication uses ``api_key`` + ``api_secret`` with a session
    token from the ICICI Direct SSO flow.
    """

    _IMPLEMENTED = True

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
        try:
            return await self._request(
                "GET",
                "/customerquote",
                params={"stock_code": stock_code, "exchange_code": exchange},
                cache_key=f"icici:quote:{stock_code}:{exchange}",
                cache_ttl=10,
            )
        except Exception as exc:
            logger.error("icici_breeze.get_quote_failed", error=str(exc))
            raise

    async def get_historical_data(
        self, stock_code: str, exchange: str, interval: str, from_date: str, to_date: str
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "GET",
                "/historicalcharts",
                params={
                    "stock_code": stock_code,
                    "exchange_code": exchange,
                    "interval": interval,
                    "from_date": from_date,
                    "to_date": to_date,
                },
                cache_key=f"icici:hist:{stock_code}:{exchange}:{interval}:{from_date}:{to_date}",
                cache_ttl=300,
            )
        except Exception as exc:
            logger.error("icici_breeze.get_historical_data_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/customerquote", params={"stock_code": "ICIBAN", "exchange_code": "NSE"})
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/customerquote"},
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
