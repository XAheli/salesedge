from __future__ import annotations

import pytest

from app.services.scoring.deal_risk_scorer import (
    DealData,
    DealRiskScorer,
    RiskScoringResult,
)


@pytest.fixture
def scorer() -> DealRiskScorer:
    return DealRiskScorer()


def _healthy_deal() -> DealData:
    """A deal with strong health signals across all dimensions."""
    return DealData(
        deal_id="DEAL-HEALTHY",
        title="Enterprise License",
        value_inr=5e7,
        initial_value_inr=4.5e7,
        stage="Negotiation",
        days_in_stage=5,
        expected_stage_days=14,
        events=[
            {"type": "email", "date": "2026-03-20"},
            {"type": "meeting", "date": "2026-03-18"},
            {"type": "call", "date": "2026-03-15"},
            {"type": "email", "date": "2026-03-12"},
            {"type": "meeting", "date": "2026-03-10"},
        ],
        baseline_event_rate=0.3,
        analysis_window_days=14,
        stakeholder_interactions={"alice": 5, "bob": 4, "carol": 3},
        total_decision_makers=3,
        sentiment_scores=[0.8, 0.6, 0.7, 0.9],
        competitor_mentions=0,
    )


def _at_risk_deal() -> DealData:
    """A deal exhibiting multiple risk signals."""
    return DealData(
        deal_id="DEAL-RISKY",
        title="Stalled Enterprise Deal",
        value_inr=3e7,
        initial_value_inr=5e7,
        stage="Proposal",
        days_in_stage=45,
        expected_stage_days=14,
        events=[{"type": "email", "date": "2026-02-01"}],
        baseline_event_rate=0.5,
        analysis_window_days=14,
        stakeholder_interactions={"alice": 1},
        total_decision_makers=4,
        sentiment_scores=[-0.3, -0.5, -0.2],
        competitor_mentions=5,
    )


class TestDealRiskScorer:
    def test_healthy_deal_low_risk(self, scorer: DealRiskScorer):
        result = scorer.score(_healthy_deal())
        assert isinstance(result, RiskScoringResult)
        assert result.risk_score < 40.0

    def test_at_risk_deal_high_risk(self, scorer: DealRiskScorer):
        result = scorer.score(_at_risk_deal())
        assert result.risk_score > 60.0

    def test_risk_in_valid_range(self, scorer: DealRiskScorer):
        for deal in [_healthy_deal(), _at_risk_deal()]:
            result = scorer.score(deal)
            assert 0.0 <= result.risk_score <= 100.0

    def test_confidence_in_valid_range(self, scorer: DealRiskScorer):
        result = scorer.score(_healthy_deal())
        assert 0.0 <= result.confidence <= 1.0

    def test_components_present(self, scorer: DealRiskScorer):
        result = scorer.score(_healthy_deal())
        assert len(result.components) == 7
        component_names = {c.name for c in result.components}
        assert "engagement_momentum" in component_names
        assert "stakeholder_coverage" in component_names
        assert "stage_velocity" in component_names

    def test_explanation_generated(self, scorer: DealRiskScorer):
        result = scorer.score(_at_risk_deal())
        assert "Risk score:" in result.explanation
        assert "Weakest areas:" in result.explanation

    def test_higher_confidence_with_more_data(self, scorer: DealRiskScorer):
        full = scorer.score(_healthy_deal())
        minimal = scorer.score(DealData(
            deal_id="DEAL-MIN",
            title="Minimal",
            value_inr=1e6,
        ))
        assert full.confidence > minimal.confidence


class TestEngagementMomentum:
    def test_high_engagement(self):
        health = DealRiskScorer.compute_engagement_momentum(
            events=[{}, {}, {}, {}, {}],
            window_days=10,
            baseline_rate=0.3,
        )
        assert health > 0.8

    def test_zero_events(self):
        health = DealRiskScorer.compute_engagement_momentum(
            events=[], window_days=14, baseline_rate=0.5,
        )
        assert health == 0.0

    def test_zero_window_returns_zero(self):
        health = DealRiskScorer.compute_engagement_momentum(
            events=[{}], window_days=0, baseline_rate=0.5,
        )
        assert health == 0.0

    def test_capped_at_one(self):
        health = DealRiskScorer.compute_engagement_momentum(
            events=[{}, {}, {}, {}, {}, {}, {}, {}, {}, {}],
            window_days=5,
            baseline_rate=0.1,
        )
        assert health == 1.0


class TestStageVelocity:
    def test_on_time(self):
        assert DealRiskScorer.compute_stage_velocity(7, 14) == 1.0

    def test_overdue(self):
        health = DealRiskScorer.compute_stage_velocity(28, 14)
        assert health < 1.0
        assert health > 0.0

    def test_severely_overdue(self):
        health = DealRiskScorer.compute_stage_velocity(100, 14)
        assert health < 0.2

    def test_zero_expected_days(self):
        assert DealRiskScorer.compute_stage_velocity(5, 0) == 0.5


class TestStakeholderEntropy:
    def test_even_distribution(self):
        interactions = {"a": 10, "b": 10, "c": 10}
        entropy = DealRiskScorer.compute_stakeholder_entropy(interactions)
        assert entropy > 0.9

    def test_single_stakeholder(self):
        entropy = DealRiskScorer.compute_stakeholder_entropy({"a": 10})
        assert entropy == 0.0

    def test_empty_interactions(self):
        entropy = DealRiskScorer.compute_stakeholder_entropy({})
        assert entropy == 0.0

    def test_skewed_distribution(self):
        interactions = {"a": 100, "b": 1, "c": 1}
        entropy = DealRiskScorer.compute_stakeholder_entropy(interactions)
        assert entropy < 0.5


class TestContractValueDrift:
    def test_value_increased(self, scorer: DealRiskScorer):
        deal = DealData(
            deal_id="UP", title="Upsell", value_inr=6e7, initial_value_inr=5e7,
        )
        result = scorer.score(deal)
        drift_comp = next(c for c in result.components if c.name == "contract_value_drift")
        assert drift_comp.health_value == 1.0

    def test_value_decreased(self, scorer: DealRiskScorer):
        deal = DealData(
            deal_id="DOWN", title="Downsell", value_inr=3e7, initial_value_inr=5e7,
        )
        result = scorer.score(deal)
        drift_comp = next(c for c in result.components if c.name == "contract_value_drift")
        assert drift_comp.health_value < 1.0

    def test_no_initial_value(self, scorer: DealRiskScorer):
        deal = DealData(
            deal_id="NOINIT", title="New", value_inr=5e7,
        )
        result = scorer.score(deal)
        drift_comp = next(c for c in result.components if c.name == "contract_value_drift")
        assert drift_comp.health_value == 0.5
