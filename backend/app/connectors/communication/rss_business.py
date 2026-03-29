from __future__ import annotations

import hashlib
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

CACHE_TTL = 900  # 15 min

ALLOWED_FEEDS: dict[str, str] = {
    "economic_times": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "livemint": "https://www.livemint.com/rss/companies",
    "moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
    "business_standard": "https://www.business-standard.com/rss/latest.rss",
    "hindu_business": "https://www.thehindubusinessline.com/feeder/default.rss",
    "financial_express": "https://www.financialexpress.com/feed/",
    "reuters_india": "https://feeds.reuters.com/reuters/INbusinessNews",
    "ndtv_business": "https://feeds.feedburner.com/ndtvprofit-latest",
}


class RSSBusinessConnector(BaseConnector):
    """Business RSS feed aggregator.

    Fetches and parses RSS/Atom feeds from a curated list of Indian
    and global business news sources.
    """

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="rss_business",
            base_url="https://rss.app",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            cache_manager=cache_manager,
            timeout=20.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def fetch_feed(
        self, feed_key: str, *, limit: int = 25
    ) -> dict[str, Any]:
        """Fetch and parse a single RSS feed by its key (from ``ALLOWED_FEEDS``)."""
        url = ALLOWED_FEEDS.get(feed_key)
        if not url:
            return {"error": f"Unknown feed key: {feed_key}", "items": []}

        cache_key = f"rss:{feed_key}"
        if self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                return cached

        resp = await self._request_raw("GET", url)
        items = self._parse_rss(resp.text, limit)
        result: dict[str, Any] = {
            "feed": feed_key,
            "url": url,
            "items": items,
            "count": len(items),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        if self.cache:
            await self.cache.set(cache_key, result, CACHE_TTL)
        return result

    async def fetch_all_feeds(
        self, *, limit_per_feed: int = 10
    ) -> dict[str, Any]:
        """Fetch all allowed feeds and merge results."""
        all_items: list[dict[str, str]] = []
        errors: list[str] = []
        for key in ALLOWED_FEEDS:
            try:
                result = await self.fetch_feed(key, limit=limit_per_feed)
                for item in result.get("items", []):
                    item["source"] = key
                all_items.extend(result.get("items", []))
            except Exception as exc:
                errors.append(f"{key}: {exc}")
                logger.warning("rss_feed_failed", feed=key, error=str(exc))

        all_items.sort(key=lambda x: x.get("published", ""), reverse=True)
        return {
            "items": all_items,
            "total": len(all_items),
            "sources": list(ALLOWED_FEEDS.keys()),
            "errors": errors,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def search_headlines(
        self, query: str, *, limit: int = 20
    ) -> dict[str, Any]:
        """Search across all feeds for headlines matching the query."""
        all_feeds = await self.fetch_all_feeds(limit_per_feed=25)
        query_lower = query.lower()
        matches = [
            item
            for item in all_feeds["items"]
            if query_lower in item.get("title", "").lower()
            or query_lower in item.get("description", "").lower()
        ]
        return {
            "query": query,
            "matches": matches[:limit],
            "total_matches": len(matches),
        }

    # ── RSS parsing ──────────────────────────────────────────────

    @staticmethod
    def _parse_rss(xml_text: str, limit: int) -> list[dict[str, str]]:
        items: list[dict[str, str]] = []
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            logger.warning("rss_parse_error")
            return items

        # RSS 2.0
        for item in root.iter("item"):
            if len(items) >= limit:
                break
            items.append(_extract_rss_item(item))

        # Atom fallback
        if not items:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            for entry in root.findall("atom:entry", ns):
                if len(items) >= limit:
                    break
                items.append(_extract_atom_entry(entry, ns))

        return items

    # ── Overrides for raw-URL fetching ───────────────────────────

    async def _get_client(self) -> Any:
        """Override to create a client without a fixed base_url."""
        import httpx

        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
            )
        return self._client

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        start = time.monotonic()
        try:
            result = await self.fetch_feed("economic_times", limit=1)
            elapsed = (time.monotonic() - start) * 1000
            return ConnectorHealth(
                status="healthy" if result.get("items") else "degraded",
                last_check=datetime.now(timezone.utc),
                response_time_ms=elapsed,
                error_rate=self.error_rate,
                details={"feeds_configured": len(ALLOWED_FEEDS)},
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
            "macro_context",
        ]


def _extract_rss_item(item: ET.Element) -> dict[str, str]:
    return {
        "title": (item.findtext("title") or "").strip(),
        "link": (item.findtext("link") or "").strip(),
        "description": (item.findtext("description") or "").strip()[:500],
        "published": (item.findtext("pubDate") or "").strip(),
    }


def _extract_atom_entry(
    entry: ET.Element, ns: dict[str, str]
) -> dict[str, str]:
    link_el = entry.find("atom:link", ns)
    return {
        "title": (entry.findtext("atom:title", default="", namespaces=ns) or "").strip(),
        "link": link_el.get("href", "") if link_el is not None else "",
        "description": (
            entry.findtext("atom:summary", default="", namespaces=ns) or ""
        ).strip()[:500],
        "published": (
            entry.findtext("atom:updated", default="", namespaces=ns) or ""
        ).strip(),
    }
