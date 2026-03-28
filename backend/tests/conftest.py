from __future__ import annotations

import asyncio
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.config import Settings, get_settings
from app.main import create_app


def _test_settings() -> Settings:
    """Build settings pointing at a local test database and Redis."""
    return Settings(
        database_url="sqlite+aiosqlite:///./test.db",
        redis_url="redis://localhost:6379/1",
        ogd_api_key="test-ogd-key",
        jwt_secret_key="test-secret",
        environment="test",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    """Create a shared async engine backed by SQLite for tests."""
    settings = _test_settings()
    eng = create_async_engine(settings.database_url, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncIterator[SQLModelAsyncSession]:
    """Yield a transactional DB session that rolls back after each test."""
    async with SQLModelAsyncSession(engine) as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    """Provide an httpx AsyncClient wired to the FastAPI app with test overrides."""
    app = create_app()

    app.dependency_overrides[get_settings] = _test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
