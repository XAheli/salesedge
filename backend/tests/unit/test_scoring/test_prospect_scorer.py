from __future__ import annotations

from datetime import datetime

import pytest

from app.services.scoring.prospect_scorer import (
    DEFAULT_WEIGHTS,
    ProspectData,
    ProspectScorer,
    ScoringResult,
)


@pytest.fixture
def scorer() -> ProspectScorer:
    return ProspectScorer()


def _perfect_prospect() -> ProspectData:
    """A prospect that should score highly across all dimensions."""
    return ProspectData(
        company_name="Ideal Tech Solutions Pvt Ltd",
        revenue_inr=2e8,
        employee_count=500,
        industry="Information Technology",
        nic_code="62011",
        state="MH",
        city="Pune",
        tech_stack=["python", "java", "kubernetes", "aws", "react", "salesforce"],
        revenue_growth_pct=30.0,
        hiring_growth_pct=20.0,
        recent_funding_inr=1e9,
        website_visits_30d=80,
        content_downloads_30d=15,
        mca_registration_date=datetime(2015, 1, 1),
        gst_filing_frequency="monthly",
        dpiit_recognized=True,
        profit_margin_pct=20.0,
        debt_equity_ratio=0.5,
        regulatory_favorability=0.9,
        listed_exchange="NSE",
    )


def _poor_prospect() -> ProspectData:
    """A prospect with minimal data that should score poorly."""
    return ProspectData(
        company_name="Unknown Co",
    )


class TestProspectScorer:
    def test_perfect_prospect_score(self, scorer: ProspectScorer):
        result = scorer.score(_perfect_prospect())
        assert isinstance(result, ScoringResult)
        assert result.score >= 70.0
        assert result.confidence >= 0.8

    def test_poor_prospect_score(self, scorer: ProspectScorer):
        result = scorer.score(_poor_prospect())
        assert result.score < 30.0
        assert result.confidence <= 0.2

    def test_score_in_valid_range(self, scorer: ProspectScorer):
        result = scorer.score(_perfect_prospect())
        assert 0.0 <= result.score <= 100.0

    def test_confidence_in_valid_range(self, scorer: ProspectScorer):
        result = scorer.score(_perfect_prospect())
        assert 0.0 <= result.confidence <= 1.0

    def test_confidence_with_missing_data(self, scorer: ProspectScorer):
        partial = ProspectData(
            company_name="Partial Data Corp",
            revenue_inr=5e8,
            industry="IT",
            state="KA",
        )
        result = scorer.score(partial)
        full = scorer.score(_perfect_prospect())
        assert result.confidence < full.confidence

    def test_feature_contributions_present(self, scorer: ProspectScorer):
        result = scorer.score(_perfect_prospect())
        assert len(result.feature_contributions) == len(DEFAULT_WEIGHTS)
        for fc in result.feature_contributions:
            assert fc.feature_name in DEFAULT_WEIGHTS
            assert 0.0 <= fc.normalised_value <= 1.0
            assert fc.weight >= 0.0

    def test_explanation_generated(self, scorer: ProspectScorer):
        result = scorer.score(_perfect_prospect())
        assert "Fit score:" in result.explanation
        assert "Top drivers:" in result.explanation

    def test_missing_data_mentioned_in_explanation(self, scorer: ProspectScorer):
        result = scorer.score(_poor_prospect())
        assert "Missing data for:" in result.explanation

    def test_batch_scoring(self, scorer: ProspectScorer):
        prospects = [_perfect_prospect(), _poor_prospect()]
        results = scorer.batch_score(prospects)
        assert len(results) == 2
        assert results[0].score > results[1].score

    def test_batch_scoring_empty(self, scorer: ProspectScorer):
        assert scorer.batch_score([]) == []


class TestIndianSpecificFeatures:
    def test_mca_registration_adds_score(self, scorer: ProspectScorer):
        with_mca = ProspectData(
            company_name="MCA Corp",
            mca_registration_date=datetime(2010, 1, 1),
        )
        without_mca = ProspectData(company_name="No MCA Corp")
        r_with = scorer.score(with_mca)
        r_without = scorer.score(without_mca)
        assert r_with.score >= r_without.score

    def test_gst_filing_frequency_monthly_best(self, scorer: ProspectScorer):
        monthly = ProspectData(
            company_name="Monthly GST",
            gst_filing_frequency="monthly",
        )
        quarterly = ProspectData(
            company_name="Quarterly GST",
            gst_filing_frequency="quarterly",
        )
        r_m = scorer.score(monthly)
        r_q = scorer.score(quarterly)
        assert r_m.score >= r_q.score

    def test_dpiit_recognized_adds_score(self, scorer: ProspectScorer):
        dpiit = ProspectData(
            company_name="DPIIT Startup",
            dpiit_recognized=True,
        )
        non_dpiit = ProspectData(
            company_name="Non DPIIT",
            dpiit_recognized=False,
        )
        r_d = scorer.score(dpiit)
        r_n = scorer.score(non_dpiit)
        assert r_d.score >= r_n.score

    def test_listed_exchange_adds_score(self, scorer: ProspectScorer):
        listed = ProspectData(
            company_name="Listed Corp",
            listed_exchange="NSE",
        )
        unlisted = ProspectData(company_name="Unlisted Corp")
        r_l = scorer.score(listed)
        r_u = scorer.score(unlisted)
        assert r_l.score >= r_u.score

    def test_target_state_preferred(self, scorer: ProspectScorer):
        target_state = ProspectData(company_name="MH Corp", state="MH")
        other_state = ProspectData(company_name="SK Corp", state="SK")
        r_t = scorer.score(target_state)
        r_o = scorer.score(other_state)
        assert r_t.score > r_o.score

    def test_target_nic_code_preferred(self, scorer: ProspectScorer):
        target_nic = ProspectData(company_name="IT Corp", nic_code="62011")
        other_nic = ProspectData(company_name="Misc Corp", nic_code="99999")
        r_t = scorer.score(target_nic)
        r_o = scorer.score(other_nic)
        assert r_t.score > r_o.score


class TestCustomWeights:
    def test_custom_weights_normalised(self):
        weights = {"company_size_fit": 1.0, "industry_fit": 1.0}
        scorer = ProspectScorer(weights=weights)
        total = sum(scorer.weights.values())
        assert abs(total - 1.0) < 1e-3

    def test_zero_weight_feature_no_contribution(self):
        weights = DEFAULT_WEIGHTS.copy()
        weights["geographic_fit"] = 0.0
        scorer = ProspectScorer(weights=weights)
        result = scorer.score(_perfect_prospect())
        geo_contrib = next(
            fc for fc in result.feature_contributions if fc.feature_name == "geographic_fit"
        )
        assert geo_contrib.weighted_contribution == 0.0
