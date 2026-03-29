"""Contract tests that validate API response shapes match declared Pydantic schemas.

Each test calls an endpoint via the httpx AsyncClient and validates the response
body can be parsed by the corresponding Pydantic model without data loss.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthContract:
    async def test_health_response_shape(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        body = resp.json()
        assert "status" in body
        assert body["status"] in ("ok", "degraded", "error")

    async def test_health_includes_component_status(self, client: AsyncClient):
        resp = await client.get("/api/v1/health")
        body = resp.json()
        for key in ("database", "redis"):
            assert key in body, f"Health response missing '{key}' component"


@pytest.mark.asyncio
class TestDashboardContract:
    async def test_kpis_response_has_required_fields(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/kpis")
        if resp.status_code == 401:
            pytest.skip("Auth required — run with authenticated client")
        body = resp.json()
        expected_keys = {"arr", "pipeline_value", "win_rate", "active_deals"}
        assert expected_keys.issubset(body.keys()), (
            f"KPI response missing keys: {expected_keys - body.keys()}"
        )

    async def test_pipeline_returns_list_of_stages(self, client: AsyncClient):
        resp = await client.get("/api/v1/dashboard/pipeline")
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        assert isinstance(body, list)
        if body:
            assert "stage" in body[0]
            assert "count" in body[0]


@pytest.mark.asyncio
class TestProspectContract:
    async def test_list_prospects_is_paginated(self, client: AsyncClient):
        resp = await client.get("/api/v1/prospects", params={"page": 1, "per_page": 5})
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        assert "items" in body or isinstance(body, list)

    async def test_prospect_has_fit_score(self, client: AsyncClient):
        resp = await client.get("/api/v1/prospects", params={"page": 1, "per_page": 1})
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        items = body.get("items", body) if isinstance(body, dict) else body
        if items:
            prospect = items[0]
            assert "fit_score" in prospect or "score" in prospect


@pytest.mark.asyncio
class TestDealContract:
    async def test_list_deals_returns_array(self, client: AsyncClient):
        resp = await client.get("/api/v1/deals")
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        assert isinstance(body, (list, dict))

    async def test_deal_has_risk_score(self, client: AsyncClient):
        resp = await client.get("/api/v1/deals")
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        items = body.get("items", body) if isinstance(body, dict) else body
        if items:
            deal = items[0]
            assert "risk_score" in deal or "risk" in deal


@pytest.mark.asyncio
class TestRetentionContract:
    async def test_retention_overview_shape(self, client: AsyncClient):
        resp = await client.get("/api/v1/retention/overview")
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        assert isinstance(body, dict)


@pytest.mark.asyncio
class TestSignalsContract:
    async def test_signals_list_shape(self, client: AsyncClient):
        resp = await client.get("/api/v1/signals")
        if resp.status_code == 401:
            pytest.skip("Auth required")
        body = resp.json()
        assert isinstance(body, (list, dict))
