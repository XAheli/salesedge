from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_LIVE = 60  # 1 min for live feed
CACHE_TTL_HISTORICAL = 3600  # 1 hour


class DhanConnector(BaseConnector):
    """Dhan API connector (v2).

    Authentication is via a JWT access-token passed in the
    ``access-token`` header.
    """

    def __init__(
        self,
        access_token: str,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="dhan",
            base_url="https://api.dhan.co/v2",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"access_token": access_token},
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._access_token = access_token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        headers["access-token"] = self._access_token
        headers.setdefault("Content-Type", "application/json")

    # ── Public methods ───────────────────────────────────────────

    async def get_market_feed_ltp(
        self, instruments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Last-traded-price feed for a list of instruments.

        Each instrument dict should contain ``exchangeSegment`` and
        ``securityId``.
        """
        return await self._request(
            "POST",
            "/marketfeed/ltp",
            json={"instruments": instruments},
        )

    async def get_quote(
        self, instruments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Full market quote for instruments."""
        return await self._request(
            "POST",
            "/marketfeed/quote",
            json={"instruments": instruments},
        )

    async def get_ohlc(
        self, instruments: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """OHLC data for instruments."""
        return await self._request(
            "POST",
            "/marketfeed/ohlc",
            json={"instruments": instruments},
        )

    async def get_option_chain(
        self, symbol: str, expiry: str
    ) -> dict[str, Any]:
        """Option chain for a symbol and expiry date (``YYYY-MM-DD``)."""
        return await self._request(
            "GET",
            "/optionchain",
            params={"symbol": symbol, "expiry": expiry},
        )

    async def get_historical_data(
        self,
        symbol: str,
        exchange: str,
        instrument_type: str,
        from_date: str,
        to_date: str,
        interval: str = "DAY",
    ) -> dict[str, Any]:
        """Historical OHLCV candles.

        Parameters
        ----------
        interval:
            One of ``1``, ``5``, ``15``, ``25``, ``60``, ``DAY``.
        """
        payload = {
            "symbol": symbol,
            "exchangeSegment": exchange,
            "instrument": instrument_type,
            "fromDate": from_date,
            "toDate": to_date,
            "interval": interval,
        }
        return await self._request(
            "POST",
            "/charts/historical",
            json=payload,
            cache_key=f"dhan:hist:{symbol}:{from_date}:{to_date}:{interval}",
            cache_ttl=CACHE_TTL_HISTORICAL,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/marketfeed/ltp", params={})
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
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
        return [
            "deal_intelligence",
            "prospect_research",
            "macro_context",
        ]
