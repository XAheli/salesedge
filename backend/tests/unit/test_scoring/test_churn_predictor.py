from __future__ import annotations

import pytest

from app.services.scoring.churn_predictor import (
    RISK_THRESHOLDS,
    ChurnPredictor,
    ChurnPrediction,
    CustomerData,
)


@pytest.fixture
def predictor() -> ChurnPredictor:
    return ChurnPredictor()


def _healthy_customer() -> CustomerData:
    """Customer with low churn risk signals."""
    return CustomerData(
        customer_id="CUST-001",
        company_name="Happy Corp Pvt Ltd",
        usage_trend_30d=0.8,
        support_ticket_frequency=0.2,
        nps_score=0.8,
        payment_delays=0.0,
        champion_turnover=0.0,
        competitive_mentions=0.0,
        contract_renewal_proximity=0.1,
        macro_headwind=0.1,
    )


def _at_risk_customer() -> CustomerData:
    """Customer with high churn risk signals."""
    return CustomerData(
        customer_id="CUST-002",
        company_name="Declining Corp Ltd",
        usage_trend_30d=-0.7,
        support_ticket_frequency=3.0,
        nps_score=-0.6,
        payment_delays=4.0,
        champion_turnover=1.0,
        competitive_mentions=5.0,
        contract_renewal_proximity=0.9,
        macro_headwind=0.8,
    )


class TestChurnPredictor:
    def test_healthy_customer_low_probability(self, predictor: ChurnPredictor):
        result = predictor.predict(_healthy_customer())
        assert isinstance(result, ChurnPrediction)
        assert result.probability < 0.3

    def test_at_risk_customer_high_probability(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        assert result.probability > 0.7

    def test_probability_in_valid_range(self, predictor: ChurnPredictor):
        for customer in [_healthy_customer(), _at_risk_customer()]:
            result = predictor.predict(customer)
            assert 0.0 <= result.probability <= 1.0

    def test_risk_level_assigned(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        assert result.risk_level in RISK_THRESHOLDS

    def test_healthy_classified_as_low(self, predictor: ChurnPredictor):
        result = predictor.predict(_healthy_customer())
        assert result.risk_level in ("low", "medium")

    def test_at_risk_classified_as_high_or_critical(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        assert result.risk_level in ("high", "critical")

    def test_contributing_factors_present(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        assert len(result.contributing_factors) > 0
        factor_names = {f[0] for f in result.contributing_factors}
        assert "champion_turnover" in factor_names

    def test_contributing_factors_sorted_by_magnitude(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        magnitudes = [abs(v) for _, v in result.contributing_factors]
        assert magnitudes == sorted(magnitudes, reverse=True)

    def test_confidence_interval_valid(self, predictor: ChurnPredictor):
        result = predictor.predict(_at_risk_customer())
        lo, hi = result.confidence_interval
        assert 0.0 <= lo <= hi <= 1.0
        assert lo <= result.probability <= hi

    def test_customer_id_preserved(self, predictor: ChurnPredictor):
        result = predictor.predict(_healthy_customer())
        assert result.customer_id == "CUST-001"
        assert result.company_name == "Happy Corp Pvt Ltd"


class TestChurnBatchPrediction:
    def test_batch_returns_correct_count(self, predictor: ChurnPredictor):
        customers = [_healthy_customer(), _at_risk_customer()]
        results = predictor.predict_batch(customers)
        assert len(results) == 2

    def test_batch_empty(self, predictor: ChurnPredictor):
        assert predictor.predict_batch([]) == []

    def test_batch_ordering_preserved(self, predictor: ChurnPredictor):
        customers = [_healthy_customer(), _at_risk_customer()]
        results = predictor.predict_batch(customers)
        assert results[0].customer_id == "CUST-001"
        assert results[1].customer_id == "CUST-002"


class TestChurnWithCustomCoefficients:
    def test_custom_coefficients_change_output(self):
        default = ChurnPredictor()
        custom = ChurnPredictor(
            coefficients={"usage_trend_30d": -2.0},
            intercept=0.0,
        )
        customer = _healthy_customer()
        r_default = default.predict(customer)
        r_custom = custom.predict(customer)
        assert r_default.probability != r_custom.probability

    def test_high_intercept_increases_base_probability(self):
        low_intercept = ChurnPredictor(intercept=-3.0)
        high_intercept = ChurnPredictor(intercept=3.0)
        customer = CustomerData(
            customer_id="ZERO", company_name="Neutral Corp",
        )
        r_low = low_intercept.predict(customer)
        r_high = high_intercept.predict(customer)
        assert r_high.probability > r_low.probability
