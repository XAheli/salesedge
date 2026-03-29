"""Idempotent ingestion deduplication.

Uses content hashing to detect and skip duplicate records across
ingestion runs.  Supports both an in-memory store and a Redis-backed
store for production.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class DeduplicationStore:
    """Content-hash-based deduplication store.

    The default implementation uses an in-memory set.  For production,
    inject a Redis client via ``redis_client``.
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        key_prefix: str = "salesedge:dedup:",
        ttl_seconds: int = 7 * 86400,  # 7 days
    ) -> None:
        self._redis = redis_client
        self._prefix = key_prefix
        self._ttl = ttl_seconds
        self._memory_store: dict[str, str] = {}  # hash → timestamp

    def compute_content_hash(self, data: dict[str, Any] | str | bytes) -> str:
        """Compute a deterministic SHA-256 hash for the given data.

        Dictionaries are serialised with sorted keys so that field order
        does not affect the hash.
        """
        if isinstance(data, dict):
            canonical = json.dumps(data, sort_keys=True, default=str)
            raw = canonical.encode("utf-8")
        elif isinstance(data, str):
            raw = data.encode("utf-8")
        else:
            raw = data

        return hashlib.sha256(raw).hexdigest()

    def is_duplicate(self, content_hash: str) -> bool:
        """Check whether this content hash has already been ingested."""
        if self._redis is not None:
            return self._check_redis(content_hash)
        return content_hash in self._memory_store

    def mark_ingested(self, content_hash: str) -> None:
        """Mark a content hash as ingested."""
        if self._redis is not None:
            self._mark_redis(content_hash)
        else:
            self._memory_store[content_hash] = datetime.utcnow().isoformat()

    def remove(self, content_hash: str) -> None:
        """Remove a hash from the dedup store (e.g. for re-ingestion)."""
        if self._redis is not None:
            self._remove_redis(content_hash)
        else:
            self._memory_store.pop(content_hash, None)

    def clear(self) -> None:
        """Clear all stored hashes.  Use with caution."""
        if self._redis is not None:
            logger.warning("dedup.clear_redis_not_supported")
        else:
            self._memory_store.clear()

    @property
    def size(self) -> int:
        """Number of hashes currently stored."""
        if self._redis is not None:
            return self._count_redis()
        return len(self._memory_store)

    # ── Redis operations ─────────────────────────────────────────────────

    def _check_redis(self, content_hash: str) -> bool:
        try:
            return bool(self._redis.exists(f"{self._prefix}{content_hash}"))
        except Exception as exc:
            logger.error("dedup.redis_check_error", error=str(exc))
            return content_hash in self._memory_store

    def _mark_redis(self, content_hash: str) -> None:
        try:
            key = f"{self._prefix}{content_hash}"
            self._redis.setex(key, self._ttl, datetime.utcnow().isoformat())
        except Exception as exc:
            logger.error("dedup.redis_mark_error", error=str(exc))
            self._memory_store[content_hash] = datetime.utcnow().isoformat()

    def _remove_redis(self, content_hash: str) -> None:
        try:
            self._redis.delete(f"{self._prefix}{content_hash}")
        except Exception as exc:
            logger.error("dedup.redis_remove_error", error=str(exc))

    def _count_redis(self) -> int:
        try:
            count = 0
            cursor = 0
            while True:
                cursor, keys = self._redis.scan(cursor, match=f"{self._prefix}*", count=100)
                count += len(keys)
                if cursor == 0:
                    break
            return count
        except Exception:
            return len(self._memory_store)
