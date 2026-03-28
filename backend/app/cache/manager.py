from __future__ import annotations

import json
import time
from collections import OrderedDict
from typing import Any, Awaitable, Callable

import redis.asyncio as aioredis


class _L1Cache:
    """In-memory LRU cache with per-entry TTL tracking."""

    def __init__(self, max_size: int = 1024) -> None:
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        expires_at = time.monotonic() + ttl
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (value, expires_at)
        while len(self._store) > self._max_size:
            self._store.popitem(last=False)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class CacheManager:
    """Two-tier cache: L1 (in-memory LRU) -> L2 (Redis) -> source callable.

    Usage::

        cache = CacheManager(redis_client)

        value = await cache.get_or_fetch(
            "prospect:123:detail",
            fetch_fn=lambda: load_prospect_from_db(123),
            ttl=300,
        )
    """

    def __init__(
        self,
        redis: aioredis.Redis,
        l1_max_size: int = 1024,
        key_prefix: str = "se:",
    ) -> None:
        self._l1 = _L1Cache(max_size=l1_max_size)
        self._redis = redis
        self._prefix = key_prefix

    def _full_key(self, key: str) -> str:
        return f"{self._prefix}{key}"

    async def get(self, key: str) -> Any | None:
        """Attempt L1 then L2 lookup. Returns None on miss."""
        l1_val = self._l1.get(key)
        if l1_val is not None:
            return l1_val

        full_key = self._full_key(key)
        raw = await self._redis.get(full_key)
        if raw is not None:
            value = json.loads(raw)
            self._l1.set(key, value, ttl=60)
            return value

        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Write to both L1 and L2."""
        self._l1.set(key, value, ttl)
        full_key = self._full_key(key)
        await self._redis.setex(full_key, ttl, json.dumps(value, default=str))

    async def invalidate(self, key: str) -> None:
        """Remove from both cache tiers."""
        self._l1.invalidate(key)
        full_key = self._full_key(key)
        await self._redis.delete(full_key)

    async def get_or_fetch(
        self,
        key: str,
        fetch_fn: Callable[[], Awaitable[Any]],
        ttl: int = 300,
    ) -> Any:
        """Cache-aside pattern: return cached value or call *fetch_fn* and cache the result."""
        cached = await self.get(key)
        if cached is not None:
            return cached

        value = await fetch_fn()
        if value is not None:
            await self.set(key, value, ttl)
        return value

    async def clear_l1(self) -> None:
        """Flush the in-memory cache only."""
        self._l1.clear()
