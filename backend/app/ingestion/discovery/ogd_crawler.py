"""OGD India auto-discovery crawler.

Crawls the Open Government Data (data.gov.in) portal to discover datasets
relevant to sales intelligence — ministry filings, economic indicators,
corporate registrations, and sector-specific data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

OGD_BASE_URL = "https://data.gov.in/api/datastore/resource"
OGD_CATALOG_URL = "https://data.gov.in/catalogs"

# Ministries with datasets relevant to sales intelligence
TARGET_MINISTRIES: list[str] = [
    "Ministry of Corporate Affairs",
    "Ministry of Commerce and Industry",
    "Ministry of Finance",
    "Ministry of Electronics and Information Technology",
    "Ministry of Statistics and Programme Implementation",
    "Ministry of MSME",
    "Ministry of Labour and Employment",
    "NITI Aayog",
    "Reserve Bank of India",
    "Securities and Exchange Board of India",
    "Department for Promotion of Industry and Internal Trade",
    "Central Board of Direct Taxes",
    "Central Board of Indirect Taxes and Customs",
]

RELEVANT_KEYWORDS: set[str] = {
    "company", "registration", "corporate", "gst", "tax", "revenue",
    "industry", "manufacturing", "startup", "msme", "employment",
    "trade", "export", "import", "investment", "fdi", "ipo",
    "financial", "banking", "insurance", "gdp", "inflation",
    "index", "production", "sector", "quarterly", "annual",
}


@dataclass
class DiscoveredDataset:
    """A dataset discovered from the OGD portal."""

    title: str
    ministry: str
    resource_id: str
    description: str = ""
    format: str = "json"
    update_frequency: str = "unknown"
    last_updated: datetime | None = None
    record_count: int | None = None
    relevance_score: float = 0.0
    url: str = ""
    tags: list[str] = field(default_factory=list)
    sector: str | None = None


@dataclass
class CoverageReport:
    """Coverage analysis across ministries and sectors."""

    total_datasets: int
    datasets_by_ministry: dict[str, int]
    datasets_by_sector: dict[str, int]
    datasets_by_frequency: dict[str, int]
    high_relevance_count: int
    coverage_gaps: list[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class OGDCrawler:
    """Crawl the OGD India portal for relevant datasets.

    In production, this makes HTTP requests to the OGD API.  The discovery
    results are used to auto-configure ingestion connectors.
    """

    def __init__(
        self,
        api_key: str | None = None,
        target_ministries: list[str] | None = None,
    ) -> None:
        self._api_key = api_key
        self._ministries = target_ministries or TARGET_MINISTRIES
        self._discovered: list[DiscoveredDataset] = []

    async def crawl_all_ministries(self) -> list[DiscoveredDataset]:
        """Crawl all target ministries and return discovered datasets."""
        logger.info(
            "ogd_crawler.crawl_start",
            ministries=len(self._ministries),
        )
        all_datasets: list[DiscoveredDataset] = []

        for ministry in self._ministries:
            try:
                datasets = await self.crawl_ministry(ministry)
                all_datasets.extend(datasets)
            except Exception as exc:
                logger.error(
                    "ogd_crawler.ministry_error",
                    ministry=ministry,
                    error=str(exc),
                )

        self._discovered = all_datasets
        logger.info(
            "ogd_crawler.crawl_complete",
            total_datasets=len(all_datasets),
        )
        return all_datasets

    async def crawl_ministry(self, ministry_name: str) -> list[DiscoveredDataset]:
        """Crawl a single ministry for relevant datasets.

        In production, this calls the OGD catalog API with pagination.
        """
        logger.info("ogd_crawler.crawl_ministry", ministry=ministry_name)

        raw_datasets = await self._fetch_ministry_catalog(ministry_name)

        discovered: list[DiscoveredDataset] = []
        for raw in raw_datasets:
            relevance = self._compute_relevance(raw)
            if relevance < 0.2:
                continue

            dataset = DiscoveredDataset(
                title=raw.get("title", ""),
                ministry=ministry_name,
                resource_id=raw.get("resource_id", ""),
                description=raw.get("description", ""),
                format=raw.get("format", "json"),
                update_frequency=raw.get("frequency", "unknown"),
                last_updated=self._parse_date(raw.get("last_updated")),
                record_count=raw.get("record_count"),
                relevance_score=round(relevance, 4),
                url=raw.get("url", ""),
                tags=raw.get("tags", []),
                sector=self._infer_sector(raw),
            )
            discovered.append(dataset)

        discovered.sort(key=lambda d: d.relevance_score, reverse=True)
        return discovered

    def build_coverage_report(self) -> CoverageReport:
        """Analyse coverage across ministries, sectors, and update frequency."""
        datasets = self._discovered

        by_ministry: dict[str, int] = {}
        by_sector: dict[str, int] = {}
        by_frequency: dict[str, int] = {}
        high_relevance = 0

        for ds in datasets:
            by_ministry[ds.ministry] = by_ministry.get(ds.ministry, 0) + 1
            if ds.sector:
                by_sector[ds.sector] = by_sector.get(ds.sector, 0) + 1
            by_frequency[ds.update_frequency] = by_frequency.get(ds.update_frequency, 0) + 1
            if ds.relevance_score >= 0.7:
                high_relevance += 1

        covered_ministries = set(by_ministry.keys())
        gaps = [m for m in self._ministries if m not in covered_ministries]

        expected_sectors = {
            "technology", "finance", "manufacturing", "healthcare",
            "energy", "infrastructure", "agriculture",
        }
        covered_sectors = set(by_sector.keys())
        sector_gaps = expected_sectors - covered_sectors

        all_gaps = gaps + [f"sector:{s}" for s in sector_gaps]

        return CoverageReport(
            total_datasets=len(datasets),
            datasets_by_ministry=by_ministry,
            datasets_by_sector=by_sector,
            datasets_by_frequency=by_frequency,
            high_relevance_count=high_relevance,
            coverage_gaps=all_gaps,
        )

    # ── Private helpers ──────────────────────────────────────────────────

    async def _fetch_ministry_catalog(
        self, ministry_name: str,
    ) -> list[dict[str, Any]]:
        """Fetch the dataset catalog for a ministry from the OGD India API."""
        if not self._api_key:
            logger.warning("ogd_crawler.no_api_key", ministry=ministry_name)
            return []

        import httpx

        logger.debug("ogd_crawler.fetching_catalog", ministry=ministry_name)
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://api.data.gov.in/lists",
                    params={
                        "format": "json",
                        "api-key": self._api_key,
                        "filters[org]": ministry_name,
                        "limit": 50,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("records", [])
                logger.warning(
                    "ogd_crawler.fetch_failed",
                    ministry=ministry_name,
                    status=resp.status_code,
                )
        except Exception as exc:
            logger.error(
                "ogd_crawler.fetch_error",
                ministry=ministry_name,
                error=str(exc),
            )
        return []

    @staticmethod
    def _compute_relevance(raw: dict[str, Any]) -> float:
        """Score how relevant a dataset is to sales intelligence."""
        text = f"{raw.get('title', '')} {raw.get('description', '')}".lower()
        tags = [t.lower() for t in raw.get("tags", [])]

        matches = sum(1 for kw in RELEVANT_KEYWORDS if kw in text)
        tag_matches = sum(1 for kw in RELEVANT_KEYWORDS if kw in tags)

        max_possible = min(len(RELEVANT_KEYWORDS), 10)
        raw_score = (matches + tag_matches * 2) / max_possible

        if raw.get("format") in ("json", "csv", "xml"):
            raw_score += 0.1
        if raw.get("frequency") in ("daily", "weekly", "monthly"):
            raw_score += 0.1
        if raw.get("record_count") and raw["record_count"] > 100:
            raw_score += 0.05

        return min(raw_score, 1.0)

    @staticmethod
    def _infer_sector(raw: dict[str, Any]) -> str | None:
        """Infer the business sector from dataset metadata."""
        text = f"{raw.get('title', '')} {raw.get('description', '')}".lower()
        sector_keywords: dict[str, list[str]] = {
            "technology": ["software", "it", "technology", "digital", "cyber"],
            "finance": ["bank", "financial", "rbi", "sebi", "insurance", "credit"],
            "manufacturing": ["manufactur", "production", "factory", "industry"],
            "healthcare": ["health", "pharma", "medical", "hospital"],
            "energy": ["energy", "power", "electricity", "renewable", "oil", "gas"],
            "infrastructure": ["infrastructure", "construction", "road", "railway"],
            "agriculture": ["agriculture", "crop", "farming", "food"],
            "trade": ["trade", "export", "import", "commerce"],
        }
        for sector, keywords in sector_keywords.items():
            if any(kw in text for kw in keywords):
                return sector
        return None

    @staticmethod
    def _parse_date(date_str: str | None) -> datetime | None:
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
