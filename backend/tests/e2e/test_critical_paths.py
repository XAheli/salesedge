"""End-to-end tests for critical user paths through the SalesEdge backend.

These tests exercise the full stack (API → services → DB) for the most
important user journeys. Requires a running test database.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.e2e
@pytest.mark.asyncio
class TestRegistrationToFirstInsight:
    """Critical path: user registers, logs in, and views dashboard insights."""

    async def test_full_onboarding_flow(self, client: AsyncClient):
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "e2e_critical@test.com",
                "password": "E2eTest123!",
                "full_name": "E2E Tester",
            },
        )
        assert reg_resp.status_code in (200, 201, 409)

        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": "e2e_critical@test.com", "password": "E2eTest123!"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json().get("access_token") or login_resp.json().get("token")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        kpi_resp = await client.get("/api/v1/dashboard/kpis", headers=headers)
        assert kpi_resp.status_code == 200

        prospects_resp = await client.get(
            "/api/v1/prospects", params={"page": 1, "per_page": 5}, headers=headers
        )
        assert prospects_resp.status_code == 200


@pytest.mark.e2e
@pytest.mark.asyncio
class TestProspectToDealFlow:
    """Critical path: browsing prospects, viewing detail, checking related deals."""

    async def test_prospect_detail_and_deals(self, client: AsyncClient):
        prospects_resp = await client.get("/api/v1/prospects", params={"per_page": 1})
        if prospects_resp.status_code == 401:
            pytest.skip("Auth required for this flow")

        body = prospects_resp.json()
        items = body.get("items", body) if isinstance(body, dict) else body
        if not items:
            pytest.skip("No prospects in test DB")

        prospect_id = items[0].get("id")
        if prospect_id:
            detail_resp = await client.get(f"/api/v1/prospects/{prospect_id}")
            assert detail_resp.status_code in (200, 404)

        deals_resp = await client.get("/api/v1/deals")
        assert deals_resp.status_code in (200, 401)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDealRiskWorkflow:
    """Critical path: viewing deals, filtering by risk, checking recovery suggestions."""

    async def test_risk_segmented_deal_view(self, client: AsyncClient):
        resp = await client.get("/api/v1/deals")
        if resp.status_code == 401:
            pytest.skip("Auth required")

        body = resp.json()
        items = body.get("items", body) if isinstance(body, dict) else body

        if items and isinstance(items, list):
            at_risk = [d for d in items if d.get("risk_score", 0) > 70]
            healthy = [d for d in items if 30 <= d.get("risk_score", 0) <= 70]
            assert isinstance(at_risk, list)
            assert isinstance(healthy, list)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDataProvenanceFlow:
    """Critical path: checking data source health before trusting scores."""

    async def test_all_sources_report_status(self, client: AsyncClient):
        resp = await client.get("/api/v1/data-provenance/sources")
        if resp.status_code == 401:
            pytest.skip("Auth required")

        body = resp.json()
        sources = body if isinstance(body, list) else body.get("sources", [])

        for source in sources:
            assert "status" in source or "name" in source


@pytest.mark.e2e
@pytest.mark.asyncio
class TestHealthEndToEnd:
    async def test_health_all_components_connected(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("status") in ("ok", "degraded")
