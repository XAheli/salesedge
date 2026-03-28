"""Deal Risk Score engine.

Implements the risk formula from Section 9.2::

    RiskScore(d) = 1 - Σⱼ wⱼ · healthⱼ(d)

A higher RiskScore means the deal is more at risk.  Individual health
components are each normalised to [0, 1] where 1 = healthy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
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

    # Engagement events in the analysis window
    events: list[dict[str, Any]] = field(default_factory=list)
    baseline_event_rate: float = 1.0  # events / day
    analysis_window_days: int = 14

    # Stakeholder interactions: {stakeholder_id: interaction_count}
    stakeholder_interactions: dict[str, int] = field(default_factory=dict)
    total_decision_makers: int = 1

    # Sentiment scores from comms (each -1 to 1)
    sentiment_scores: list[float] = field(default_factory=list)

    # Competitor signals
    competitor_mentions: int = 0


@dataclass
class RiskComponent:
    """A single health component and its contribution to the risk score."""

    name: str
    health_value: float
    weight: float
    weighted_health: float


@dataclass
class RiskScoringResult:
    """Output of the deal risk-scoring engine."""

    risk_score: float
    confidence: float
    components: list[RiskComponent]
    explanation: str
    scored_at: datetime = field(default_factory=datetime.utcnow)


DEFAULT_RISK_WEIGHTS: dict[str, float] = {
    "engagement_momentum": 0.20,
    "stakeholder_coverage": 0.15,
    "stage_velocity": 0.20,
    "sentiment_trend": 0.15,
    "competitor_presence": 0.10,
    "contract_value_drift": 0.10,
    "stakeholder_entropy": 0.10,
}


class DealRiskScorer:
    """Score the risk level of a sales deal."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_RISK_WEIGHTS.copy()
        total = sum(self.weights.values())
        if not math.isclose(total, 1.0, rel_tol=1e-3):
            self.weights = {k: v / total for k, v in self.weights.items()}

    def score(self, deal: DealData) -> RiskScoringResult:
        """Score a single deal and return a full risk breakdown."""
        health_fns: dict[str, float] = {
            "engagement_momentum": self.compute_engagement_momentum(
                deal.events, deal.analysis_window_days, deal.baseline_event_rate,
            ),
            "stakeholder_coverage": self._compute_stakeholder_coverage(deal),
            "stage_velocity": self.compute_stage_velocity(
                deal.days_in_stage, deal.expected_stage_days,
            ),
            "sentiment_trend": self._compute_sentiment_health(deal.sentiment_scores),
            "competitor_presence": self._compute_competitor_health(deal.competitor_mentions),
            "contract_value_drift": self._compute_value_drift_health(deal),
            "stakeholder_entropy": self._compute_entropy_health(deal.stakeholder_interactions),
        }

        components: list[RiskComponent] = []
        weighted_health_sum = 0.0

        for name, health in health_fns.items():
            w = self.weights.get(name, 0.0)
            wh = w * health
            weighted_health_sum += wh
            components.append(RiskComponent(
                name=name, health_value=round(health, 4),
                weight=w, weighted_health=round(wh, 4),
            ))

        risk = round(min(max((1.0 - weighted_health_sum) * 100, 0.0), 100.0), 2)
        confidence = self._estimate_confidence(deal)
        explanation = self._build_explanation(components, risk)

        return RiskScoringResult(
            risk_score=risk,
            confidence=round(confidence, 4),
            components=components,
            explanation=explanation,
        )

    # ── Component calculators ────────────────────────────────────────────

    @staticmethod
    def compute_engagement_momentum(
        events: list[dict[str, Any]],
        window_days: int,
        baseline_rate: float,
    ) -> float:
        """Health = recent event rate / expected baseline rate, capped at 1."""
        if window_days <= 0 or baseline_rate <= 0:
            return 0.0
        actual_rate = len(events) / window_days
        return min(actual_rate / baseline_rate, 1.0)

    @staticmethod
    def compute_stakeholder_entropy(interactions: dict[str, int]) -> float:
        """Shannon entropy of stakeholder interaction distribution.

        Higher entropy means engagement is more evenly spread (healthier).
        Returns normalised entropy in [0, 1].
        """
        if not interactions:
            return 0.0
        total = sum(interactions.values())
        if total == 0:
            return 0.0
        n = len(interactions)
        if n <= 1:
            return 0.0
        entropy = 0.0
        for count in interactions.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        max_entropy = math.log2(n)
        return entropy / max_entropy if max_entropy > 0 else 0.0

    @staticmethod
    def compute_stage_velocity(days_in_stage: int, expected_days: int) -> float:
        """Health based on how long the deal has lingered vs. expectation.

        Returns 1.0 when on-time, decays towards 0 the further behind.
        """
        if expected_days <= 0:
            return 0.5
        ratio = days_in_stage / expected_days
        if ratio <= 1.0:
            return 1.0
        return max(1.0 / ratio, 0.0)

    # ── Private helpers ──────────────────────────────────────────────────

    def _compute_stakeholder_coverage(self, deal: DealData) -> float:
        engaged = len(deal.stakeholder_interactions)
        total = max(deal.total_decision_makers, 1)
        return min(engaged / total, 1.0)

    @staticmethod
    def _compute_sentiment_health(scores: list[float]) -> float:
        """Map average sentiment [-1, 1] to health [0, 1]."""
        if not scores:
            return 0.5
        avg = sum(scores) / len(scores)
        return (avg + 1.0) / 2.0

    @staticmethod
    def _compute_competitor_health(mentions: int) -> float:
        """Fewer competitor mentions = healthier. Decays from 1 as mentions grow."""
        return 1.0 / (1.0 + mentions)

    @staticmethod
    def _compute_value_drift_health(deal: DealData) -> float:
        """Health = current / initial value ratio capped at 1. Dropping value = risk."""
        if not deal.initial_value_inr or deal.initial_value_inr <= 0:
            return 0.5
        ratio = deal.value_inr / deal.initial_value_inr
        return min(max(ratio, 0.0), 1.0)

    def _compute_entropy_health(self, interactions: dict[str, int]) -> float:
        return self.compute_stakeholder_entropy(interactions)

    @staticmethod
    def _estimate_confidence(deal: DealData) -> float:
        signals = 0
        total = 5
        if deal.events:
            signals += 1
        if deal.stakeholder_interactions:
            signals += 1
        if deal.sentiment_scores:
            signals += 1
        if deal.initial_value_inr is not None:
            signals += 1
        if deal.expected_stage_days > 0:
            signals += 1
        return max(signals / total, 0.1)

    @staticmethod
    def _build_explanation(components: list[RiskComponent], risk: float) -> str:
        sorted_c = sorted(components, key=lambda c: c.health_value)
        weakest = sorted_c[:3]
        parts = [f"Risk score: {risk}/100."]
        parts.append("Weakest areas: " + ", ".join(
            f"{c.name} (health={c.health_value:.2f})" for c in weakest
        ))
        return " ".join(parts)
