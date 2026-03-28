from __future__ import annotations

import csv
import io
import time
from datetime import datetime, timezone
from typing import Any

import structlog
from bs4 import BeautifulSoup

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL_DEFAULT = 86_400  # 24 hours — RBI updates infrequently


class RBIDBIEConnector(BaseConnector):
    """RBI Database on Indian Economy (DBIE) connector.

    RBI does not expose a formal REST API.  Data is extracted via HTML
    scraping and CSV download parsing from https://data.rbi.org.in.
    """

    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    SERIES_MAP = {
        "policy_rates": "/DBIE/dbie.rbi?site=publications#!4",
        "cpi": "/DBIE/dbie.rbi?site=publications#!5_1",
        "forex_reserves": "/DBIE/dbie.rbi?site=publications#!17",
        "bank_credit": "/DBIE/dbie.rbi?site=publications#!10",
        "reference_rates": "/DBIE/dbie.rbi?site=publications#!41",
    }

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="rbi_dbie",
            base_url="https://data.rbi.org.in",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            cache_manager=cache_manager,
            timeout=45.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def get_policy_rates(self) -> dict[str, Any]:
        """Latest RBI policy rates (repo, reverse repo, CRR, SLR, MSF, bank rate)."""
        cache_key = "rbi:policy_rates"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/DBIE/dbie.rbi",
            params={"site": "statistics", "page": "keyrates"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_policy_rates_html(resp.text)
        if self.cache and data:
            await self.cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    async def get_cpi_data(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """CPI inflation time-series data."""
        cache_key = f"rbi:cpi:{start_date}:{end_date}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/DBIE/dbie.rbi",
            params={"site": "statistics", "page": "cpi"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "CPI")
        if start_date or end_date:
            data["records"] = self._filter_by_date(
                data.get("records", []), start_date, end_date
            )
        if self.cache and data:
            await self.cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    async def get_forex_reserves(self) -> dict[str, Any]:
        """Latest foreign exchange reserves."""
        cache_key = "rbi:forex_reserves"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/DBIE/dbie.rbi",
            params={"site": "statistics", "page": "forexreserves"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "Forex Reserves")
        if self.cache and data:
            await self.cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    async def get_bank_credit_growth(
        self, sector: str | None = None
    ) -> dict[str, Any]:
        """Sectoral bank credit growth data."""
        cache_key = f"rbi:bank_credit:{sector or 'all'}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/DBIE/dbie.rbi",
            params={"site": "statistics", "page": "bankcredit"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "Bank Credit")
        if sector and data.get("records"):
            data["records"] = [
                r for r in data["records"]
                if sector.lower() in str(r).lower()
            ]
        if self.cache and data:
            await self.cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    async def get_reference_rates(self) -> dict[str, Any]:
        """RBI reference rates for USD/INR, EUR/INR, GBP/INR, JPY/INR."""
        cache_key = "rbi:reference_rates"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/DBIE/dbie.rbi",
            params={"site": "statistics", "page": "referencerates"},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_table_page(resp.text, "Reference Rates")
        if self.cache and data:
            await self.cache.set(cache_key, data, CACHE_TTL_DEFAULT)
        return data

    # ── Parsing helpers ──────────────────────────────────────────

    @staticmethod
    def _parse_policy_rates_html(html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        rates: dict[str, str | None] = {}
        table = soup.find("table")
        if not table:
            return {"rates": rates, "source": "rbi_dbie", "parsed_at": datetime.now(timezone.utc).isoformat()}

        for row in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 2:
                label = cells[0].lower()
                value = cells[-1]
                if "repo" in label and "reverse" not in label:
                    rates["repo_rate"] = value
                elif "reverse repo" in label:
                    rates["reverse_repo_rate"] = value
                elif "crr" in label or "cash reserve" in label:
                    rates["crr"] = value
                elif "slr" in label or "statutory liquidity" in label:
                    rates["slr"] = value
                elif "msf" in label or "marginal standing" in label:
                    rates["msf_rate"] = value
                elif "bank rate" in label:
                    rates["bank_rate"] = value

        return {
            "rates": rates,
            "source": "rbi_dbie",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _parse_table_page(html: str, label: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all("table")
        records: list[dict[str, str]] = []
        column_names: list[str] = []

        for table in tables:
            header_row = table.find("tr")
            if not header_row:
                continue
            headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            if not headers:
                continue
            column_names = headers
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if cells and len(cells) == len(headers):
                    records.append(dict(zip(headers, cells)))
            if records:
                break

        return {
            "label": label,
            "columns": column_names,
            "records": records,
            "record_count": len(records),
            "source": "rbi_dbie",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _parse_csv_content(content: str) -> list[dict[str, str]]:
        reader = csv.DictReader(io.StringIO(content))
        return list(reader)

    @staticmethod
    def _filter_by_date(
        records: list[dict[str, str]],
        start_date: str | None,
        end_date: str | None,
    ) -> list[dict[str, str]]:
        filtered = []
        for r in records:
            date_val = r.get("Date") or r.get("date") or r.get("Period") or ""
            if start_date and date_val < start_date:
                continue
            if end_date and date_val > end_date:
                continue
            filtered.append(r)
        return filtered

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            resp = await self._request_raw(
                "GET", "/", headers=self.BROWSER_HEADERS
            )
            elapsed = (time.monotonic() - start) * 1000
            ok = resp.status_code == 200
            return ConnectorHealth(
                status="healthy" if ok else "degraded",
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
            "industry_sizing",
            "prospect_research",
            "territory_planning",
        ]
