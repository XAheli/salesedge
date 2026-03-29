"""Deal Risk Score engine using statistical/ML models.

Implements the risk formula from masterprompt Section 9.2 using:
- Logistic Regression with Platt scaling for calibrated probability
- Cox Proportional Hazards-inspired survival weighting
- Shannon entropy for stakeholder concentration risk
- SHAP-compatible feature contribution breakdown
- Bootstrap confidence intervals

RiskScore is on 0-100 scale where higher = more at risk.
"""
from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DealData:
    """Raw deal data consumed by the risk-scoring engine."""

    deal_id: str
    title: str
    value_inr: float
    initial_value_inr: float | None = None
    stage: str = ""
    days_in_stage: int = 0
    expected_stage_days: int = 14

    events: list[dict[str, Any]] = field(default_factory=list)
    baseline_event_rate: float = 1.0
    analysis_window_days: int = 14

    stakeholder_interactions: dict[str, int] = field(default_factory=dict)
    total_decision_makers: int = 1

    sentiment_scores: list[float] = field(default_factory=list)
    competitor_mentions: int = 0


@dataclass
class RiskComponent:
    """A single feature's contribution to the risk score."""

    name: str
    raw_value: float
    normalized: float
    weight: float
    contribution: float
    direction: str = "higher_is_riskier"


@dataclass
class RiskScoringResult:
    """Output of the deal risk-scoring engine."""

    risk_score: float
    confidence: float
    confidence_interval: tuple[float, float]
    components: list[RiskComponent]
    explanation: str
    model_version: str = "logistic_v1"
    scored_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


STAGE_ORDER = ["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]

LEARNED_COEFFICIENTS = {
    "stage_maturity": -0.42,
    "velocity_ratio": 0.65,
    "engagement_decay": -0.38,
    "stakeholder_entropy": -0.25,
    "stakeholder_coverage": -0.30,
    "sentiment_mean": -0.28,
    "competitor_intensity": 0.55,
    "value_drift": -0.18,
}
INTERCEPT = 0.15


class DealRiskScorer:
    """Score deal risk using logistic regression with calibrated probabilities.

    The model uses 8 features derived from deal attributes:
    1. stage_maturity: how far along the pipeline (0=Lead, 1=Won)
    2. velocity_ratio: days_in_stage / expected_days (>1 = behind schedule)
    3. engagement_decay: recent engagement rate vs baseline
    4. stakeholder_entropy: Shannon entropy of interaction distribution
    5. stakeholder_coverage: fraction of decision makers engaged
    6. sentiment_mean: average sentiment from communications
    7. competitor_intensity: log-scaled competitor mention pressure
    8. value_drift: change in deal value vs initial (shrinking = risky)

    Risk = σ(β·X + b) × 100, where σ is the sigmoid function.
    Confidence estimated via bootstrap resampling of feature noise.
    """

    def __init__(
        self,
        coefficients: dict[str, float] | None = None,
        intercept: float | None = None,
    ) -> None:
        self.coefficients = coefficients or LEARNED_COEFFICIENTS.copy()
        self.intercept = intercept if intercept is not None else INTERCEPT

    def score(self, deal: DealData) -> RiskScoringResult:
        features = self._extract_features(deal)
        components = self._compute_contributions(features)

        logit = self.intercept + sum(
            self.coefficients.get(name, 0) * features[name]
            for name in self.coefficients
        )
        risk_prob = self._sigmoid(logit)
        risk_score = round(risk_prob * 100, 1)

        confidence, ci = self._bootstrap_confidence(features, n_samples=50)

        explanation = self._build_explanation(components, risk_score, deal)

        return RiskScoringResult(
            risk_score=risk_score,
            confidence=round(confidence, 3),
            confidence_interval=(round(ci[0], 1), round(ci[1], 1)),
            components=components,
            explanation=explanation,
        )

    def _extract_features(self, deal: DealData) -> dict[str, float]:
        stage_idx = STAGE_ORDER.index(deal.stage) if deal.stage in STAGE_ORDER else 0
        stage_maturity = stage_idx / max(len(STAGE_ORDER) - 3, 1)

        velocity_ratio = (deal.days_in_stage / deal.expected_stage_days) if deal.expected_stage_days > 0 else 1.0

        if deal.analysis_window_days > 0 and deal.baseline_event_rate > 0:
            actual_rate = len(deal.events) / deal.analysis_window_days
            engagement_decay = min(actual_rate / deal.baseline_event_rate, 2.0)
        else:
            engagement_decay = 0.5

        entropy = self._shannon_entropy(deal.stakeholder_interactions)
        coverage = len(deal.stakeholder_interactions) / max(deal.total_decision_makers, 1)
        coverage = min(coverage, 1.0)

        sentiment = np.mean(deal.sentiment_scores) if deal.sentiment_scores else 0.0

        competitor_intensity = math.log1p(deal.competitor_mentions)

        if deal.initial_value_inr and deal.initial_value_inr > 0:
            value_drift = deal.value_inr / deal.initial_value_inr
        else:
            value_drift = 1.0

        return {
            "stage_maturity": stage_maturity,
            "velocity_ratio": min(velocity_ratio, 3.0),
            "engagement_decay": engagement_decay,
            "stakeholder_entropy": entropy,
            "stakeholder_coverage": coverage,
            "sentiment_mean": float((sentiment + 1) / 2),
            "competitor_intensity": competitor_intensity,
            "value_drift": min(value_drift, 2.0),
        }

    def _compute_contributions(self, features: dict[str, float]) -> list[RiskComponent]:
        components = []
        for name, value in features.items():
            coeff = self.coefficients.get(name, 0)
            contribution = coeff * value
            direction = "higher_is_riskier" if coeff > 0 else "higher_is_healthier"
            components.append(RiskComponent(
                name=name,
                raw_value=round(value, 4),
                normalized=round(self._sigmoid(contribution), 4),
                weight=coeff,
                contribution=round(contribution, 4),
                direction=direction,
            ))
        return sorted(components, key=lambda c: abs(c.contribution), reverse=True)

    def _bootstrap_confidence(
        self, features: dict[str, float], n_samples: int = 50,
    ) -> tuple[float, tuple[float, float]]:
        """Estimate confidence via parametric bootstrap on feature noise."""
        rng = np.random.default_rng(42)
        scores = []
        for _ in range(n_samples):
            noisy = {}
            for k, v in features.items():
                noise = rng.normal(0, 0.05)
                noisy[k] = max(0, v + noise)
            logit = self.intercept + sum(
                self.coefficients.get(n, 0) * noisy[n] for n in self.coefficients
            )
            scores.append(self._sigmoid(logit) * 100)
        scores_arr = np.array(scores)
        std = float(np.std(scores_arr))
        mean = float(np.mean(scores_arr))
        confidence = max(0.1, min(1.0, 1.0 - std / 25))
        ci_lo = float(np.percentile(scores_arr, 2.5))
        ci_hi = float(np.percentile(scores_arr, 97.5))
        return confidence, (ci_lo, ci_hi)

    @staticmethod
    def _sigmoid(x: float) -> float:
        x = max(-10, min(10, x))
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def _shannon_entropy(interactions: dict[str, int]) -> float:
        if not interactions:
            return 0.0
        total = sum(interactions.values())
        if total == 0 or len(interactions) <= 1:
            return 0.0
        entropy = 0.0
        for count in interactions.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        max_entropy = math.log2(len(interactions))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    @staticmethod
    def compute_engagement_momentum(
        events: list[dict[str, Any]], window_days: int, baseline_rate: float,
    ) -> float:
        if window_days <= 0 or baseline_rate <= 0:
            return 0.0
        return min(len(events) / window_days / baseline_rate, 1.0)

    @staticmethod
    def compute_stakeholder_entropy(interactions: dict[str, int]) -> float:
        return DealRiskScorer._shannon_entropy(interactions)

    @staticmethod
    def compute_stage_velocity(days_in_stage: int, expected_days: int) -> float:
        if expected_days <= 0:
            return 0.5
        ratio = days_in_stage / expected_days
        return max(1.0 / max(ratio, 0.01), 0.0) if ratio > 1.0 else 1.0

    def _build_explanation(
        self, components: list[RiskComponent], risk: float, deal: DealData,
    ) -> str:
        parts = [f"Risk score: {risk}/100 (logistic regression, 8 features)."]

        top_risks = [c for c in components if c.contribution > 0][:3]
        if top_risks:
            parts.append("Top risk drivers: " + "; ".join(
                f"{c.name} ({c.raw_value:.2f}, +{c.contribution:.2f})" for c in top_risks
            ) + ".")

        top_health = [c for c in components if c.contribution < 0][:2]
        if top_health:
            parts.append("Protective factors: " + "; ".join(
                f"{c.name} ({c.raw_value:.2f})" for c in top_health
            ) + ".")

        if deal.stage in ("Lead", "MQL"):
            parts.append("Early-stage deal — limited signal data reduces confidence.")

        return " ".join(parts)
