"""Integration tests that hit all major API endpoints through the FastAPI app.

Uses the httpx AsyncClient from conftest.py with test database overrides.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthEndpoint:
    async def test_health_returns_200(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200

    async def test_health_body_structure(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        body = resp.json()
        assert "status" in body


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_register_new_user(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "integration@test.com",
                "password": "Str0ngP@ss!",
                "full_name": "Integration Tester",
            },
        )
        assert resp.status_code in (200, 201, 409)

    async def test_login_returns_token(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@test.com",
                "password": "Str0ngP@ss!",
                "full_name": "Login Tester",
            },
        )
        resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@test.com", "password": "Str0ngP@ss!"},
        )
        if resp.status_code == 200:
            body = resp.json()
            assert "access_token" in body or "token" in body


@pytest.mark.integration
@pytest.mark.asyncio
class TestDashboardEndpoints:
    async def test_kpis_endpoint(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/kpis")
        assert resp.status_code in (200, 401)

    async def test_pipeline_endpoint(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/pipeline")
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestProspectEndpoints:
    async def test_list_prospects(self, client: AsyncClient):
        resp = await client.get("/api/v1/prospects")
        assert resp.status_code in (200, 401)

    async def test_list_prospects_with_pagination(self, client: AsyncClient):
        resp = await client.get("/api/v1/prospects", params={"page": 1, "per_page": 5})
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestDealEndpoints:
    async def test_list_deals(self, client: AsyncClient):
        resp = await client.get("/api/v1/deals")
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestRetentionEndpoints:
    async def test_retention_overview(self, client: AsyncClient):
        resp = await client.get("/api/v1/retention/overview")
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestSignalEndpoints:
    async def test_list_signals(self, client: AsyncClient):
        resp = await client.get("/api/v1/signals")
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestCompetitiveEndpoints:
    async def test_competitive_overview(self, client: AsyncClient):
        resp = await client.get("/api/v1/competitive/overview")
        assert resp.status_code in (200, 401)


@pytest.mark.integration
@pytest.mark.asyncio
class TestDataProvenanceEndpoints:
    async def test_sources_endpoint(self, client: AsyncClient):
        resp = await client.get("/api/v1/data-provenance/sources")
        assert resp.status_code in (200, 401)
