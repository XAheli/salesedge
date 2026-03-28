from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_LIVE = 300  # 5 min for live/quote data
CACHE_TTL_HISTORICAL = 3600  # 1 hour for historical data


class NSEConnector(BaseConnector):
    """NSE India connector.

    NSE requires browser-like headers and active session cookies.
    A pre-flight GET to the main page is performed to obtain the
    cookies before making API calls.
    """

    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/",
    }

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="nse",
            base_url="https://www.nseindia.com",
            tier=ConnectorTier.TIER2_EXCHANGE,
            cache_manager=cache_manager,
            timeout=30.0,
        )
        self._cookies: httpx.Cookies | None = None
        self._cookie_ts: float = 0.0

    # ── Session / cookie management ──────────────────────────────

    async def _ensure_session(self) -> None:
        """Hit the NSE homepage to obtain session cookies if stale (> 4 min)."""
        if self._cookies and (time.monotonic() - self._cookie_ts < 240):
            return
        client = await self._get_client()
        resp = await client.get(
            "/", headers=self.BROWSER_HEADERS, follow_redirects=True
        )
        self._cookies = resp.cookies
        self._cookie_ts = time.monotonic()
        self._log.debug("nse_session_refreshed")

    async def _nse_get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        cache_key: str | None = None,
        cache_ttl: int = CACHE_TTL_LIVE,
    ) -> dict[str, Any]:
        """NSE-specific GET with session cookies and browser headers."""
        if cache_key and self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        await self._ensure_session()

        client = await self._get_client()
        start = time.monotonic()
        resp = await client.get(
            path,
            params=params or {},
            headers=self.BROWSER_HEADERS,
            cookies=self._cookies,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        self._request_count += 1
        self._total_response_time_ms += elapsed_ms

        if resp.status_code == 401 or resp.status_code == 403:
            self._cookies = None
            await self._ensure_session()
            resp = await client.get(
                path,
                params=params or {},
                headers=self.BROWSER_HEADERS,
                cookies=self._cookies,
            )

        if resp.status_code >= 400:
            self._error_count += 1
            self._circuit.record_failure()
            from app.connectors.base import UpstreamError

            raise UpstreamError(resp.status_code, resp.text[:500], self.name)

        self._circuit.record_success()
        data = resp.json()
        if cache_key and self.cache:
            await self.cache.set(cache_key, data, cache_ttl)
        return data

    # ── Public methods ───────────────────────────────────────────

    async def get_quote(self, symbol: str) -> dict[str, Any]:
        """Real-time quote for a symbol."""
        symbol = symbol.upper()
        return await self._nse_get(
            "/api/quote-equity",
            {"symbol": symbol},
            cache_key=f"nse:quote:{symbol}",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_index_data(
        self, index: str = "NIFTY 50"
    ) -> dict[str, Any]:
        """Index constituents and live value."""
        return await self._nse_get(
            "/api/equity-stockIndices",
            {"index": index},
            cache_key=f"nse:index:{index.replace(' ', '_')}",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_option_chain(self, symbol: str) -> dict[str, Any]:
        """Full option chain for a symbol."""
        symbol = symbol.upper()
        return await self._nse_get(
            "/api/option-chain-equities",
            {"symbol": symbol},
            cache_key=f"nse:oc:{symbol}",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_market_status(self) -> dict[str, Any]:
        """Current market open/close status."""
        return await self._nse_get(
            "/api/marketStatus",
            cache_key="nse:market_status",
            cache_ttl=60,
        )

    async def get_fii_dii_data(self) -> dict[str, Any]:
        """FII and DII activity data."""
        return await self._nse_get(
            "/api/fiidiiActivity",
            cache_key="nse:fii_dii",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_historical_data(
        self,
        symbol: str,
        from_date: str,
        to_date: str,
        *,
        series: str = "EQ",
    ) -> dict[str, Any]:
        """Historical OHLCV data for a symbol.

        Date format: ``dd-mm-yyyy``.
        """
        symbol = symbol.upper()
        params: dict[str, Any] = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date,
            "series": f'["{series}"]',
        }
        ck = self._ck("hist", {"s": symbol, "f": from_date, "t": to_date})
        return await self._nse_get(
            "/api/historical/cm/equity",
            params,
            cache_key=ck,
            cache_ttl=CACHE_TTL_HISTORICAL,
        )

    async def get_top_gainers(self) -> dict[str, Any]:
        """Today's top gainers across indices."""
        return await self._nse_get(
            "/api/live-analysis-variations",
            {"index": "gainers"},
            cache_key="nse:gainers",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_top_losers(self) -> dict[str, Any]:
        """Today's top losers across indices."""
        return await self._nse_get(
            "/api/live-analysis-variations",
            {"index": "losers"},
            cache_key="nse:losers",
            cache_ttl=CACHE_TTL_LIVE,
        )

    async def get_advances_declines(self) -> dict[str, Any]:
        """Advance/decline ratio across market segments."""
        return await self._nse_get(
            "/api/market-data-pre-open",
            {"key": "ALL"},
            cache_key="nse:adv_dec",
            cache_ttl=CACHE_TTL_LIVE,
        )

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            data = await self.get_market_status()
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"market_status": data},
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
            "deal_intelligence",
        ]

    # ── Helpers ──────────────────────────────────────────────────

    @staticmethod
    def _ck(prefix: str, params: dict[str, Any]) -> str:
        raw = f"nse:{prefix}:{sorted(params.items())}"
        digest = hashlib.md5(raw.encode(), usedforsecurity=False).hexdigest()[:12]
        return f"nse:{prefix}:{digest}"
