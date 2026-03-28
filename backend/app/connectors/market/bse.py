from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL = 300  # 5 min


class BSEConnector(BaseConnector):
    """BSE India connector.

    Provides equity scrip data, index information, and gainers/losers
    from the Bombay Stock Exchange API.
    """

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="bse",
            base_url="https://api.bseindia.com/BseIndiaAPI/api",
            tier=ConnectorTier.TIER2_EXCHANGE,
            cache_manager=cache_manager,
            timeout=30.0,
        )

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        headers.setdefault(
            "User-Agent",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        )
        headers.setdefault("Referer", "https://www.bseindia.com/")
        headers.setdefault("Accept", "application/json")

    # ── Public methods ───────────────────────────────────────────

    async def get_scrip_data(self, scrip_code: str) -> dict[str, Any]:
        """Detailed quote for a BSE scrip code."""
        return await self._request(
            "GET",
            "/getScripHeaderData/Equity",
            params={"Ession_Flag": "Session", "Deession_Flag": "Day", "scripcode": scrip_code},
            cache_key=f"bse:scrip:{scrip_code}",
            cache_ttl=CACHE_TTL,
        )

    async def get_index_data(
        self, index: str = "SENSEX"
    ) -> dict[str, Any]:
        """BSE index live data."""
        return await self._request(
            "GET",
            "/Abordsearch/Getstockdata",
            params={"indexcode": index, "period": "D"},
            cache_key=f"bse:index:{index}",
            cache_ttl=CACHE_TTL,
        )

    async def get_gainers_losers(
        self, *, gl_type: str = "gainer"
    ) -> dict[str, Any]:
        """Top gainers or losers.  *gl_type* is ``gainer`` or ``loser``."""
        return await self._request(
            "GET",
            "/MktRGainerLoser/w",
            params={"GLtype": gl_type, "ExchType": "BSE", "Flag": "0"},
            cache_key=f"bse:gl:{gl_type}",
            cache_ttl=CACHE_TTL,
        )

    async def get_market_cap(self) -> dict[str, Any]:
        """Market capitalisation summary."""
        return await self._request(
            "GET",
            "/MarketCap/w",
            cache_key="bse:marketcap",
            cache_ttl=CACHE_TTL,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_index_data("SENSEX")
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if data else "degraded",
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
            "prospect_research",
            "macro_context",
            "competitive_intelligence",
        ]
