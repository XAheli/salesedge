from __future__ import annotations

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every request/response cycle.

    If the incoming request already carries an X-Request-ID header the value is
    preserved; otherwise a new UUID4 is generated.  The ID is stored on
    ``request.state.request_id`` for downstream handlers and echoed back on
    the response.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(_HEADER) or str(uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[_HEADER] = request_id
        return response
