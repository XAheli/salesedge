from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

import structlog
from bs4 import BeautifulSoup

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL = 86_400  # 24 hours


class MCAConnector(BaseConnector):
    """Ministry of Corporate Affairs (MCA) company data connector.

    MCA does not expose a public REST API.  Data is extracted via HTML
    scraping of the MCA portal.
    """

    BROWSER_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="mca",
            base_url="https://www.mca.gov.in",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            cache_manager=cache_manager,
            timeout=45.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def search_company(self, name: str) -> dict[str, Any]:
        """Search for a company by name and return registration details."""
        cache_key = f"mca:search:{name.lower().replace(' ', '_')}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/mcafoportal/viewCompanyMasterData.do",
            params={"companyName": name},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_search_results(resp.text)
        if self.cache and data.get("results"):
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    async def get_company_details(self, cin: str) -> dict[str, Any]:
        """Detailed company information by Corporate Identification Number."""
        cache_key = f"mca:company:{cin}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/mcafoportal/viewCompanyMasterData.do",
            params={"companyID": cin},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_company_detail(resp.text, cin)
        if self.cache and data.get("cin"):
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    async def get_director_details(self, din: str) -> dict[str, Any]:
        """Director details by Director Identification Number."""
        cache_key = f"mca:director:{din}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw(
            "GET",
            "/mcafoportal/viewDirectorMasterData.do",
            params={"directorID": din},
            headers=self.BROWSER_HEADERS,
        )
        data = self._parse_director_detail(resp.text, din)
        if self.cache and data.get("din"):
            await self.cache.set(cache_key, data, CACHE_TTL)
        return data

    # ── Parsing helpers ──────────────────────────────────────────

    @staticmethod
    def _parse_search_results(html: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        results: list[dict[str, str]] = []

        table = soup.find("table", {"id": "companyList"}) or soup.find("table")
        if table:
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) >= 3:
                    results.append({
                        "cin": cells[0],
                        "company_name": cells[1],
                        "status": cells[2] if len(cells) > 2 else "",
                        "roc": cells[3] if len(cells) > 3 else "",
                    })

        return {
            "results": results,
            "count": len(results),
            "source": "mca",
            "parsed_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _parse_company_detail(html: str, cin: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        details: dict[str, str] = {"cin": cin}

        field_map = {
            "company name": "company_name",
            "roc code": "roc",
            "registration number": "registration_number",
            "category": "category",
            "sub category": "sub_category",
            "class of company": "company_class",
            "date of incorporation": "incorporation_date",
            "authorised capital": "authorised_capital",
            "paid up capital": "paid_up_capital",
            "registered address": "registered_address",
            "email": "email",
            "listing status": "listing_status",
            "activity description": "activity",
        }

        for row in soup.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 2:
                label = cells[0].lower().strip().rstrip(":")
                for key_fragment, field_name in field_map.items():
                    if key_fragment in label:
                        details[field_name] = cells[1]
                        break

        details["source"] = "mca"
        details["parsed_at"] = datetime.now(timezone.utc).isoformat()
        return details

    @staticmethod
    def _parse_director_detail(html: str, din: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "lxml")
        details: dict[str, str] = {"din": din}

        for row in soup.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 2:
                label = cells[0].lower().strip()
                if "name" in label:
                    details["name"] = cells[1]
                elif "designation" in label:
                    details["designation"] = cells[1]
                elif "appointment" in label:
                    details["appointment_date"] = cells[1]

        details["source"] = "mca"
        details["parsed_at"] = datetime.now(timezone.utc).isoformat()
        return details

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
            "prospect_research",
            "competitive_intelligence",
            "territory_planning",
        ]
