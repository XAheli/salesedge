"""Unified cross-entity search service.

Searches across prospects, deals, signals, and data sources with
relevance scoring, filtering, and pagination.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

import structlog

logger = structlog.get_logger(__name__)

EntityType = Literal["prospects", "deals", "signals", "data_sources"]

ALL_ENTITY_TYPES: list[EntityType] = ["prospects", "deals", "signals", "data_sources"]


@dataclass
class SearchHit:
    """A single search result."""

    entity_type: str
    entity_id: str
    title: str
    snippet: str
    relevance_score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    highlight_fields: list[str] = field(default_factory=list)


@dataclass
class SearchResults:
    """Paginated search results across entity types."""

    query: str
    hits: list[SearchHit]
    total_count: int
    entity_counts: dict[str, int]
    page: int = 1
    page_size: int = 20
    search_time_ms: float = 0.0
    searched_at: datetime = field(default_factory=datetime.utcnow)


class UnifiedSearch:
    """Cross-entity search service.

    In production this delegates to a search backend (Elasticsearch,
    PostgreSQL full-text, or Typesense). This implementation provides the
    interface and an in-memory reference implementation.
    """

    def __init__(self) -> None:
        self._index: dict[str, list[dict[str, Any]]] = {
            et: [] for et in ALL_ENTITY_TYPES
        }

    # ── Public API ───────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        entity_types: list[EntityType] | None = None,
        limit: int = 20,
        offset: int = 0,
        filters: dict[str, Any] | None = None,
    ) -> SearchResults:
        """Search across entities matching the query string.

        Parameters
        ----------
        query : free-text search query
        entity_types : restrict to specific entity types
        limit : max results to return
        offset : pagination offset
        filters : additional field-level filters
        """
        start = datetime.utcnow()
        types = entity_types or ALL_ENTITY_TYPES
        filters = filters or {}

        all_hits: list[SearchHit] = []
        entity_counts: dict[str, int] = {}

        for et in types:
            hits = self._search_entity_type(query, et, filters)
            entity_counts[et] = len(hits)
            all_hits.extend(hits)

        all_hits.sort(key=lambda h: h.relevance_score, reverse=True)
        total = len(all_hits)
        paginated = all_hits[offset: offset + limit]

        elapsed = (datetime.utcnow() - start).total_seconds() * 1000

        logger.info(
            "search.executed",
            query=query,
            types=types,
            total=total,
            returned=len(paginated),
            time_ms=round(elapsed, 2),
        )

        return SearchResults(
            query=query,
            hits=paginated,
            total_count=total,
            entity_counts=entity_counts,
            page=(offset // limit) + 1 if limit > 0 else 1,
            page_size=limit,
            search_time_ms=round(elapsed, 2),
        )

    def index_document(
        self,
        entity_type: EntityType,
        entity_id: str,
        title: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add or update a document in the in-memory search index."""
        docs = self._index.setdefault(entity_type, [])
        existing = next((d for d in docs if d["id"] == entity_id), None)
        doc = {
            "id": entity_id,
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "indexed_at": datetime.utcnow().isoformat(),
        }
        if existing:
            docs.remove(existing)
        docs.append(doc)

    def remove_document(self, entity_type: EntityType, entity_id: str) -> bool:
        """Remove a document from the index."""
        docs = self._index.get(entity_type, [])
        before = len(docs)
        self._index[entity_type] = [d for d in docs if d["id"] != entity_id]
        return len(self._index[entity_type]) < before

    def get_index_stats(self) -> dict[str, int]:
        """Return the count of indexed documents per entity type."""
        return {et: len(docs) for et, docs in self._index.items()}

    # ── Private helpers ──────────────────────────────────────────────────

    def _search_entity_type(
        self,
        query: str,
        entity_type: str,
        filters: dict[str, Any],
    ) -> list[SearchHit]:
        docs = self._index.get(entity_type, [])
        query_lower = query.lower()
        tokens = query_lower.split()
        hits: list[SearchHit] = []

        for doc in docs:
            if not self._passes_filters(doc, filters):
                continue

            score = self._compute_relevance(
                query_lower, tokens, doc["title"], doc["content"],
            )
            if score > 0:
                snippet = self._extract_snippet(query_lower, doc["content"])
                highlight = self._find_highlight_fields(query_lower, doc)
                hits.append(SearchHit(
                    entity_type=entity_type,
                    entity_id=doc["id"],
                    title=doc["title"],
                    snippet=snippet,
                    relevance_score=round(score, 4),
                    metadata=doc.get("metadata", {}),
                    highlight_fields=highlight,
                ))

        return hits

    @staticmethod
    def _compute_relevance(
        query: str,
        tokens: list[str],
        title: str,
        content: str,
    ) -> float:
        """Simple TF-based relevance scoring."""
        title_lower = title.lower()
        content_lower = content.lower()
        score = 0.0

        if query in title_lower:
            score += 10.0
        if query in content_lower:
            score += 3.0

        for token in tokens:
            if token in title_lower:
                score += 5.0
            count = content_lower.count(token)
            score += min(count * 1.0, 5.0)

        return score

    @staticmethod
    def _extract_snippet(query: str, content: str, max_len: int = 200) -> str:
        idx = content.lower().find(query)
        if idx == -1:
            return content[:max_len] + ("..." if len(content) > max_len else "")
        start = max(0, idx - 50)
        end = min(len(content), idx + len(query) + 150)
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet

    @staticmethod
    def _find_highlight_fields(query: str, doc: dict[str, Any]) -> list[str]:
        fields: list[str] = []
        if query in doc.get("title", "").lower():
            fields.append("title")
        if query in doc.get("content", "").lower():
            fields.append("content")
        meta = doc.get("metadata", {})
        for key, val in meta.items():
            if isinstance(val, str) and query in val.lower():
                fields.append(f"metadata.{key}")
        return fields

    @staticmethod
    def _passes_filters(doc: dict[str, Any], filters: dict[str, Any]) -> bool:
        meta = doc.get("metadata", {})
        for key, expected in filters.items():
            actual = meta.get(key)
            if actual is None:
                return False
            if isinstance(expected, list):
                if actual not in expected:
                    return False
            elif actual != expected:
                return False
        return True
