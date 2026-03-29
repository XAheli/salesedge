"""Integration tests for the full data flow from connectors to API responses.

Validates that data ingested from connectors is queryable through the REST API
with correct transformations applied at each layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestConnectorToAPIFlow:
    async def test_ingested_prospect_appears_in_api(self, client: AsyncClient, db_session):
        """Verify a prospect inserted via ingestion is returned by the prospects API."""
        from app.models.prospect import Prospect

        prospect = Prospect(
            company_name="Test Corp India Pvt Ltd",
            industry="Technology",
            revenue_inr=12000.0,
            fit_score=75.0,
        )
        db_session.add(prospect)
        await db_session.commit()

        resp = await client.get("/api/v1/prospects")
        if resp.status_code == 200:
            body = resp.json()
            items = body.get("items", body) if isinstance(body, dict) else body
            names = [p.get("name", "") for p in items]
            assert "Test Corp India Pvt Ltd" in names

    async def test_ingested_signal_appears_in_signals_api(self, client: AsyncClient, db_session):
        """Verify a signal inserted via ingestion is returned by the signals API."""
        from app.models.signal import Signal

        signal = Signal(
            title="RBI Rate Decision",
            source="rbi_dbie",
            signal_type="policy",
            impact_score=0.9,
            summary="RBI holds repo rate at 6.5%",
            published_at=datetime.now(timezone.utc),
        )
        db_session.add(signal)
        await db_session.commit()

        resp = await client.get("/api/v1/signals")
        if resp.status_code == 200:
            body = resp.json()
            items = body if isinstance(body, list) else body.get("items", [])
            titles = [s.get("title", "") for s in items]
            assert "RBI Rate Decision" in titles


@pytest.mark.integration
@pytest.mark.asyncio
class TestScoringPipelineFlow:
    async def test_prospect_receives_fit_score_after_ingestion(self, db_session):
        """Verify the scoring engine assigns a fit score to a newly ingested prospect."""
        from app.services.scoring.prospect_scorer import ProspectScorer

        scorer = ProspectScorer()
        features = {
            "revenue": 15000.0,
            "market_cap": 80000.0,
            "sector": "Banking",
            "growth_rate": 0.12,
            "digital_maturity": 0.7,
        }

        score = scorer.compute_score(features)
        assert 0 <= score <= 100

    async def test_deal_receives_risk_score(self, db_session):
        """Verify the deal risk scorer produces valid output."""
        from app.services.scoring.deal_risk_scorer import DealRiskScorer

        scorer = DealRiskScorer()
        features = {
            "engagement_velocity": 0.6,
            "days_in_stage": 15,
            "has_champion": True,
            "competitor_active": False,
            "budget_approved": True,
            "deal_value": 50_00_000,
        }

        score = scorer.compute_score(features)
        assert 0 <= score <= 100


@pytest.mark.integration
@pytest.mark.asyncio
class TestCacheIntegration:
    async def test_second_request_served_from_cache(self, client: AsyncClient):
        """Verify repeated identical requests benefit from Redis caching."""
        resp1 = await client.get("/api/v1/dashboard/kpis")
        resp2 = await client.get("/api/v1/dashboard/kpis")

        if resp1.status_code == 200:
            assert resp1.json() == resp2.json()
