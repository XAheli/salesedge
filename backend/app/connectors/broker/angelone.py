from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class AngelOneConnector(BaseConnector):
    """Angel One SmartAPI connector.

    Authentication requires ``api_key``, ``client_id``, and a TOTP-based
    session token.
    """

    _IMPLEMENTED = True

    def __init__(
        self,
        api_key: str,
        client_id: str,
        access_token: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="angelone",
            base_url="https://apiconnect.angelone.in/rest",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"api_key": api_key, "client_id": client_id},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._access_token = access_token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        headers["X-PrivateKey"] = self.auth_config.get("api_key", "")
        headers["X-ClientLocalIP"] = "127.0.0.1"
        headers["X-MACAddress"] = "00:00:00:00:00:00"
        headers.setdefault("Content-Type", "application/json")

    async def get_quote(self, symbol_token: str, exchange: str = "NSE") -> dict[str, Any]:
        try:
            return await self._request(
                "POST",
                "/secure/angelbroking/order/v1/getLtpData",
                json={
                    "exchange": exchange,
                    "tradingsymbol": symbol_token,
                    "symboltoken": symbol_token,
                },
                cache_key=f"angelone:quote:{symbol_token}:{exchange}",
                cache_ttl=10,
            )
        except Exception as exc:
            logger.error("angelone.get_quote_failed", error=str(exc))
            raise

    async def get_historical_data(
        self, symbol_token: str, exchange: str, interval: str, from_date: str, to_date: str
    ) -> dict[str, Any]:
        try:
            return await self._request(
                "POST",
                "/secure/angelbroking/order/v1/getCandleData",
                json={
                    "exchange": exchange,
                    "symboltoken": symbol_token,
                    "interval": interval,
                    "fromdate": from_date,
                    "todate": to_date,
                },
                cache_key=f"angelone:hist:{symbol_token}:{exchange}:{interval}:{from_date}:{to_date}",
                cache_ttl=300,
            )
        except Exception as exc:
            logger.error("angelone.get_historical_data_failed", error=str(exc))
            raise

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request(
                "POST",
                "/secure/angelbroking/order/v1/getLtpData",
                json={"exchange": "NSE", "tradingsymbol": "SBIN-EQ", "symboltoken": "3045"},
            )
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"endpoint": "/secure/angelbroking/order/v1/getLtpData"},
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
