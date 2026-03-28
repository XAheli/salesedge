from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class ZerodhaConnector(BaseConnector):
    """Zerodha Kite Connect API connector.

    Authentication uses the Kite Connect OAuth 2.0 flow.  The
    ``access_token`` must be obtained separately via the login flow
    and refreshed daily.

    Rate limit: **10 requests/second**.
    """

    def __init__(
        self,
        api_key: str,
        access_token: str | None = None,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="zerodha",
            base_url="https://api.kite.trade",
            tier=ConnectorTier.TIER2_EXCHANGE,
            auth_config={"api_key": api_key},
            rate_limit=10,
            cache_manager=cache_manager,
            timeout=15.0,
        )
        self._api_key = api_key
        self._access_token = access_token

    def set_access_token(self, token: str) -> None:
        self._access_token = token

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        if self._access_token:
            headers["Authorization"] = f"token {self._api_key}:{self._access_token}"
        headers.setdefault("X-Kite-Version", "3")

    # ── Public methods ───────────────────────────────────────────

    async def get_quote(
        self, instruments: list[str]
    ) -> dict[str, Any]:
        """Full quote for one or more instruments (e.g. ``NSE:RELIANCE``)."""
        params = {"i": instruments}
        return await self._request(
            "GET",
            "/quote",
            params=params,
            cache_key=f"zerodha:quote:{self._instruments_key(instruments)}",
            cache_ttl=60,
        )

    async def get_historical_data(
        self,
        instrument_token: str,
        interval: str,
        from_date: str,
        to_date: str,
        *,
        continuous: bool = False,
        oi: bool = False,
    ) -> dict[str, Any]:
        """Historical candle data.

        Parameters
        ----------
        interval:
            ``minute``, ``3minute``, ``5minute``, ``15minute``,
            ``30minute``, ``60minute``, ``day``, ``week``, ``month``.
        """
        params: dict[str, Any] = {
            "from": from_date,
            "to": to_date,
        }
        if continuous:
            params["continuous"] = 1
        if oi:
            params["oi"] = 1

        ck = self._ck("hist", {"t": instrument_token, "i": interval, "f": from_date, "t2": to_date})
        return await self._request(
            "GET",
            f"/instruments/historical/{instrument_token}/{interval}",
            params=params,
            cache_key=ck,
            cache_ttl=3600,
        )

    async def get_instruments(
        self, exchange: str | None = None
    ) -> dict[str, Any]:
        """Download the full instrument list (CSV-backed, cached 24 h)."""
        path = "/instruments"
        if exchange:
            path = f"/instruments/{exchange}"
        return await self._request(
            "GET",
            path,
            cache_key=f"zerodha:instruments:{exchange or 'all'}",
            cache_ttl=86_400,
        )

    async def get_ltp(
        self, instruments: list[str]
    ) -> dict[str, Any]:
        """Last traded price for instruments."""
        return await self._request(
            "GET",
            "/quote/ltp",
            params={"i": instruments},
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            await self._request("GET", "/user/margins")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
            )
        except Exception as exc:
            elapsed = (time.monotonic() - start) * 1000
            status = "degraded" if "token" in str(exc).lower() else "unhealthy"
            return ConnectorHealth(
                status=status,
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

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _instruments_key(instruments: list[str]) -> str:
        raw = ",".join(sorted(instruments))
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:10]

    @staticmethod
    def _ck(prefix: str, params: dict[str, Any]) -> str:
        raw = f"zerodha:{prefix}:{sorted(params.items())}"
        return hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]
