from __future__ import annotations

import logging
import re
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("salesedge.audit")

_SENSITIVE_KEYS = re.compile(
    r"(password|secret|token|api_key|apikey|authorization|credit_card|ssn|pan_number)",
    re.IGNORECASE,
)
_REDACTED = "***REDACTED***"

_MAX_BODY_LOG = 2048


def _redact(obj: Any) -> Any:
    """Recursively redact sensitive keys from dicts and lists."""
    if isinstance(obj, dict):
        return {
            k: (_REDACTED if _SENSITIVE_KEYS.search(k) else _redact(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact(item) for item in obj]
    return obj


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware that records every request/response cycle.

    Logs method, path, user identity (if available via ``request.state.user_id``),
    response status code, and duration.  Request/response payloads are
    truncated and have sensitive fields redacted before logging.

    Parameters
    ----------
    app:
        The ASGI application.
    log_request_body:
        Whether to log (redacted) request bodies for non-GET requests.
    skip_paths:
        Paths to exclude from audit logging (e.g., health checks).
    """

    def __init__(
        self,
        app,  # type: ignore[override]
        log_request_body: bool = False,
        skip_paths: set[str] | None = None,
    ) -> None:
        super().__init__(app)
        self.log_request_body = log_request_body
        self.skip_paths: set[str] = skip_paths or {"/health", "/healthz"}

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.skip_paths:
            return await call_next(request)

        start = time.monotonic()
        user_id = getattr(request.state, "user_id", None) or "anonymous"
        request_id = getattr(request.state, "request_id", None) or "-"

        body_snippet: str | None = None
        if self.log_request_body and request.method not in ("GET", "HEAD", "OPTIONS"):
            try:
                raw = await request.body()
                text = raw[:_MAX_BODY_LOG].decode("utf-8", errors="replace")
                import json

                try:
                    parsed = json.loads(text)
                    body_snippet = str(_redact(parsed))[:_MAX_BODY_LOG]
                except json.JSONDecodeError:
                    body_snippet = text[:_MAX_BODY_LOG]
            except Exception:
                body_snippet = "<unreadable>"

        response: Response | None = None
        error_msg: str | None = None
        try:
            response = await call_next(request)
        except Exception as exc:
            error_msg = str(exc)
            raise
        finally:
            duration_ms = (time.monotonic() - start) * 1000
            status = response.status_code if response else 500

            entry = {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) or None,
                "user_id": user_id,
                "status": status,
                "duration_ms": round(duration_ms, 2),
                "client_ip": (
                    request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
                    or (request.client.host if request.client else "unknown")
                ),
            }

            if body_snippet:
                entry["body"] = body_snippet
            if error_msg:
                entry["error"] = error_msg

            if status >= 500:
                logger.error("audit %s", entry)
            elif status >= 400:
                logger.warning("audit %s", entry)
            else:
                logger.info("audit %s", entry)

        return response
