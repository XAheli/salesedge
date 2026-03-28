from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog
from bs4 import BeautifulSoup

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL = 43_200  # 12 hours


class SEBIConnector(BaseConnector):
    """SEBI data connector.

    SEBI does not provide a public REST API.  Data is obtained by
    scraping / downloading from the SEBI website.
    """

    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    }

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="sebi",
            base_url="https://www.sebi.gov.in",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            cache_manager=cache_manager,
            timeout=45.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def get_fii_data(self) -> dict[str, Any]:
        """FII / FPI investment flow data."""
        cache_key = "sebi:fii_data"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/sebiweb/other/OtherAction.do",
            params={"doRecognisedFpi": "yes", "type": "fpi"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_fii_page(resp.text)
        if self.cache:
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    async def get_mutual_fund_data(self) -> dict[str, Any]:
        """Aggregate mutual-fund industry data from SEBI."""
        cache_key = "sebi:mf_data"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/sebiweb/other/OtherAction.do",
            params={"doMutualFund": "yes"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "Mutual Fund")
        if self.cache:
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    async def get_ipo_data(self) -> dict[str, Any]:
        """Recent IPO filings and status."""
        cache_key = "sebi:ipo_data"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/sebiweb/other/OtherAction.do",
            params={"doIPO": "yes"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "IPO")
        if self.cache:
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    async def get_regulatory_updates(
        self, *, limit: int = 20
    ) -> dict[str, Any]:
        """Latest SEBI circulars and regulatory updates."""
        cache_key = f"sebi:circulars:{limit}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/sebiweb/home/HomeAction.do",
            params={"doListing": "yes", "sid": "1", "ssid": "1"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_circulars(resp.text, limit)
        if self.cache:
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    # ── Parsing helpers ──────────────────────────────────────────

    @staticmethod
    def _parse_fii_page(html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        records: list[dict[str, str]] = []
        table = soup.find("table")
        if table:
            headers: list[str] = []
            for row in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in row.find_all(["th", "td"])]
                if not headers:
                    headers = cells
                    continue
                if cells and len(cells) == len(headers):
                    records.append(dict(zip(headers, cells)))
        return {
            "type": "fii_fpi",
            "records": records,
            "record_count": len(records),
            "source": "sebi",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _parse_table_page(html: str, label: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        records: list[dict[str, str]] = []
        for table in soup.find_all("table"):
            header_row = table.find("tr")
            if not header_row:
                continue
            headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            if not headers:
                continue
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if cells and len(cells) == len(headers):
                    records.append(dict(zip(headers, cells)))
            if records:
                break
        return {
            "label": label,
            "records": records,
            "record_count": len(records),
            "source": "sebi",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _parse_circulars(html: str, limit: int) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        circulars: list[dict[str, str]] = []
        for item in soup.find_all("a", href=True):
            text = item.get_text(strip=True)
            if text and len(text) > 20:
                circulars.append({
                    "title": text,
                    "url": item["href"],
                })
                if len(circulars) >= limit:
                    break
        return {
            "circulars": circulars,
            "count": len(circulars),
            "source": "sebi",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            resp = await self._request_raw(
                "GET", "/", headers=self.BROWSER_HEADERS
            )
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if resp.status_code == 200 else "degraded",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"status_code": resp.status_code},
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
            "macro_context",
            "prospect_research",
            "competitive_intelligence",
        ]
