from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from app.api.middleware.request_id import RequestIDMiddleware
from app.api.v1.router import v1_router
from app.config import get_settings
from app.models.user import User  # noqa: F401

_engine: AsyncEngine | None = None
_redis: aioredis.Redis | None = None


def get_engine() -> AsyncEngine:
    """Return the global async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.async_database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=3,
        )
    return _engine


def get_redis_pool() -> aioredis.Redis:
    """Return the global Redis connection pool."""
    global _redis
    if _redis is None:
        settings = get_settings()
        _redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=50,
        )
    return _redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown of DB engine and Redis pool."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    redis = get_redis_pool()
    app.state.db_engine = engine
    app.state.redis = redis

    yield

    await redis.aclose()
    await engine.dispose()


def create_app() -> FastAPI:
    """Application factory — builds and configures the FastAPI instance."""
    settings = get_settings()

    app = FastAPI(
        title="SalesEdge API",
        description="Intelligent Sales & Revenue Operations Platform",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    if settings.environment == "production":
        from app.api.middleware.auth import JWTAuthMiddleware
        app.add_middleware(JWTAuthMiddleware)

    app.include_router(v1_router, prefix="/api/v1")

    from app.api.websocket.deal_alerts import router as ws_alerts_router
    from app.api.websocket.data_updates import router as ws_data_router
    app.include_router(ws_alerts_router)
    app.include_router(ws_data_router)

    @app.get("/", tags=["root"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "salesedge-api", "version": "1.0.0"}

    return app


app = create_app()
