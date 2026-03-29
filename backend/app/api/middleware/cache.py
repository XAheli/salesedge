from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

_DEFAULT_TTL = 60
_REDIS_URL_ENV = "REDIS_URL"
_CACHE_HEADER = "X-Cache"

_redis_client: Any | None = None


def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    try:
        import redis

        url = os.environ.get(_REDIS_URL_ENV, "redis://localhost:6379/0")
        _redis_client = redis.from_url(url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception:
        logger.warning("Redis unavailable — response caching disabled")
        return None


def _cache_key(request: Request) -> str:
    raw = f"{request.method}:{request.url.path}:{request.url.query}"
    return f"salesedge:cache:{hashlib.sha256(raw.encode()).hexdigest()}"


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """Redis-backed response cache with per-route configurable TTL.

    Only caches GET requests.  Responses are stored as JSON in Redis and
    served with an ``X-Cache: HIT`` or ``X-Cache: MISS`` header.  If Redis is
    unreachable the middleware degrades gracefully and passes requests through.

    Parameters
    ----------
    app:
        The ASGI application.
    default_ttl:
        Default cache TTL in seconds (default 60).
    route_ttls:
        Mapping of path prefixes to TTL overrides.
    """

    def __init__(
        self,
        app,  # type: ignore[override]
        default_ttl: int = _DEFAULT_TTL,
        route_ttls: dict[str, int] | None = None,
    ) -> None:
        super().__init__(app)
        self.default_ttl = default_ttl
        self.route_ttls = route_ttls or {}

    def _ttl_for(self, path: str) -> int:
        for prefix, ttl in self.route_ttls.items():
            if path.startswith(prefix):
                return ttl
        return self.default_ttl

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method != "GET":
            return await call_next(request)

        r = _get_redis()
        if r is None:
            return await call_next(request)

        key = _cache_key(request)

        try:
            cached = r.get(key)
        except Exception:
            cached = None

        if cached is not None:
            try:
                payload = json.loads(cached)
                response = JSONResponse(
                    content=payload["body"],
                    status_code=payload["status_code"],
                )
                response.headers[_CACHE_HEADER] = "HIT"
                return response
            except (json.JSONDecodeError, KeyError):
                pass

        response = await call_next(request)

        if 200 <= response.status_code < 300:
            body_parts: list[bytes] = []
            async for chunk in response.body_iterator:  # type: ignore[attr-defined]
                body_parts.append(chunk if isinstance(chunk, bytes) else chunk.encode())
            body_bytes = b"".join(body_parts)

            try:
                body_json = json.loads(body_bytes)
                ttl = self._ttl_for(request.url.path)
                r.setex(
                    key,
                    ttl,
                    json.dumps({"status_code": response.status_code, "body": body_json}),
                )
            except Exception:
                pass

            response = Response(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        response.headers[_CACHE_HEADER] = "MISS"
        return response
