from __future__ import annotations

from typing import Any

import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings

_AUTH_HEADER = "Authorization"
_BEARER_PREFIX = "Bearer "

_PUBLIC_PATHS: set[str] = {
    "/",
    "/health",
    "/healthz",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
}


def _decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """JWT bearer-token authentication middleware.

    Extracts the ``Authorization: Bearer <token>`` header, validates the JWT,
    and stores the decoded claims on ``request.state.user``.  Requests to
    public paths (health checks, docs) are passed through without auth.

    Parameters
    ----------
    app:
        The ASGI application.
    public_paths:
        Additional paths that bypass authentication.
    """

    def __init__(self, app, public_paths: set[str] | None = None) -> None:  # type: ignore[override]
        super().__init__(app)
        self.public_paths = _PUBLIC_PATHS | (public_paths or set())

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in self.public_paths or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get(_AUTH_HEADER)
        if not auth_header or not auth_header.startswith(_BEARER_PREFIX):
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "Missing or malformed Authorization header.",
                    },
                },
            )

        token = auth_header[len(_BEARER_PREFIX) :]

        try:
            claims = _decode_token(token)
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "TOKEN_EXPIRED",
                        "message": "Token has expired. Please re-authenticate.",
                    },
                },
            )
        except jwt.InvalidTokenError as exc:
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": f"Invalid token: {exc}",
                    },
                },
            )

        request.state.user = claims
        request.state.user_id = claims.get("sub")

        return await call_next(request)
