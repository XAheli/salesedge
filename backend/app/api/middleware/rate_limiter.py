from __future__ import annotations

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

_DEFAULT_RATE = 100
_DEFAULT_WINDOW = 60


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter.

    Tracks requests per client IP within a configurable time window.
    In production, replace the in-memory store with Redis for multi-process
    consistency.

    Parameters
    ----------
    app:
        The ASGI application.
    rate:
        Maximum requests allowed per window (default 100).
    window:
        Window duration in seconds (default 60).
    """

    def __init__(self, app, rate: int = _DEFAULT_RATE, window: int = _DEFAULT_WINDOW) -> None:  # type: ignore[override]
        super().__init__(app)
        self.rate = rate
        self.window = window
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _prune(self, key: str, now: float) -> None:
        cutoff = now - self.window
        self._hits[key] = [ts for ts in self._hits[key] if ts > cutoff]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        key = self._client_key(request)
        now = time.monotonic()
        self._prune(key, now)

        if len(self._hits[key]) >= self.rate:
            retry_after = int(self.window - (now - self._hits[key][0]))
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": {
                        "code": "RATE_LIMITED",
                        "message": f"Rate limit exceeded. Try again in {max(1, retry_after)}s.",
                    },
                },
                headers={"Retry-After": str(max(1, retry_after))},
            )

        self._hits[key].append(now)
        return await call_next(request)
