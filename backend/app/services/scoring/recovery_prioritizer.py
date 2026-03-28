"""Recovery Priority Score engine.

Implements Section 9.4::

    RecoveryPriority(d) = RiskScore(d) × ContractValue(d) × RecoverabilityEstimate(d)

Deals are ranked by this composite score so that sales leadership focuses
recovery effort where it matters most.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DealWithRisk:
    """A deal that has already been risk-scored."""

    deal_id: str
    title: str
    risk_score: float           # 0-100
    value_inr: float
    stage: str = ""
    days_in_stage: int = 0
    owner: str | None = None
    champion_exists: bool = True
    multi_threaded: bool = False
    engagement_events_7d: int = 0
    competitor_mentions: int = 0
    relationship_strength: float = 0.5   # 0-1
    executive_sponsor: bool = False


@dataclass
class RecoveryAction:
    """A recommended recovery action."""

    action: str
    priority: str  # critical, high, medium, low
    rationale: str
    expected_impact: str


@dataclass
class PrioritizedDeal:
    """A deal with its recovery priority score and recommended actions."""

    deal_id: str
    title: str
    risk_score: float
    value_inr: float
    recoverability: float
    recovery_priority: float
    rank: int
    recommended_actions: list[RecoveryAction]
    scored_at: datetime = field(default_factory=datetime.utcnow)


# Normalisation constants for contract value (INR)
VALUE_SCALE_INR = 1e8  # 10 Cr as the reference "large deal"

# Stage recoverability priors
STAGE_RECOVERABILITY: dict[str, float] = {
    "discovery": 0.9,
    "qualification": 0.85,
    "proposal": 0.7,
    "negotiation": 0.6,
    "verbal_commit": 0.4,
    "closed_lost": 0.1,
}


class RecoveryPrioritizer:
    """Rank at-risk deals by recovery priority."""

    def prioritize(self, deals: list[DealWithRisk]) -> list[PrioritizedDeal]:
        """Score and rank deals for recovery effort allocation."""
        scored: list[PrioritizedDeal] = []

        for deal in deals:
            recoverability = self.estimate_recoverability(deal)
            norm_value = self._normalise_value(deal.value_inr)
            risk_factor = deal.risk_score / 100.0

            priority = round(risk_factor * norm_value * recoverability * 100, 2)

            actions = self._generate_actions(deal, recoverability)
            scored.append(PrioritizedDeal(
                deal_id=deal.deal_id,
                title=deal.title,
                risk_score=deal.risk_score,
                value_inr=deal.value_inr,
                recoverability=round(recoverability, 4),
                recovery_priority=priority,
                rank=0,
                recommended_actions=actions,
            ))

        scored.sort(key=lambda d: d.recovery_priority, reverse=True)
        for idx, deal in enumerate(scored, start=1):
            deal.rank = idx

        return scored

    def estimate_recoverability(self, deal: DealWithRisk) -> float:
        """Estimate how likely a deal is to be recovered given its current state.

        Combines stage-based priors with relationship signals.
        """
        stage_prior = STAGE_RECOVERABILITY.get(deal.stage.lower(), 0.5)

        signals: list[float] = [stage_prior]

        if deal.champion_exists:
            signals.append(0.8)
        else:
            signals.append(0.2)

        if deal.multi_threaded:
            signals.append(0.7)
        else:
            signals.append(0.3)

        if deal.engagement_events_7d > 0:
            engagement_score = min(deal.engagement_events_7d / 5.0, 1.0)
            signals.append(engagement_score)

        competitor_penalty = 1.0 / (1.0 + deal.competitor_mentions * 0.3)
        signals.append(competitor_penalty)

        signals.append(deal.relationship_strength)

        if deal.executive_sponsor:
            signals.append(0.85)

        return sum(signals) / len(signals) if signals else 0.5

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _normalise_value(value_inr: float) -> float:
        """Log-scale normalisation of deal value."""
        if value_inr <= 0:
            return 0.0
        return min(math.log1p(value_inr) / math.log1p(VALUE_SCALE_INR), 1.0)

    @staticmethod
    def _generate_actions(
        deal: DealWithRisk,
        recoverability: float,
    ) -> list[RecoveryAction]:
        actions: list[RecoveryAction] = []

        if not deal.champion_exists:
            actions.append(RecoveryAction(
                action="Identify and develop a new champion within the buying committee",
                priority="critical",
                rationale="No internal champion — deal lacks advocacy",
                expected_impact="Restores internal support and deal momentum",
            ))

        if not deal.multi_threaded:
            actions.append(RecoveryAction(
                action="Multi-thread: engage additional stakeholders beyond primary contact",
                priority="high",
                rationale="Single-threaded deals are fragile to contact changes",
                expected_impact="Reduces dependency risk and broadens consensus",
            ))

        if deal.engagement_events_7d == 0:
            actions.append(RecoveryAction(
                action="Re-engage with a value-driven touchpoint (case study, ROI analysis)",
                priority="high",
                rationale="Zero engagement in the last 7 days signals deal stalling",
                expected_impact="Re-activates buyer interest and pipeline momentum",
            ))

        if deal.competitor_mentions > 2:
            actions.append(RecoveryAction(
                action="Deploy competitive battlecard and schedule differentiation session",
                priority="high",
                rationale=f"{deal.competitor_mentions} competitor mentions detected",
                expected_impact="Strengthens positioning against active competitors",
            ))

        if not deal.executive_sponsor and deal.value_inr > 5e7:
            actions.append(RecoveryAction(
                action="Request executive sponsor alignment meeting",
                priority="medium",
                rationale="High-value deal without executive-level engagement",
                expected_impact="Signals organisational commitment and accelerates decisions",
            ))

        if not actions:
            actions.append(RecoveryAction(
                action="Continue current engagement cadence; monitor for signal changes",
                priority="low",
                rationale="No critical gaps identified in current deal motion",
                expected_impact="Maintains healthy deal trajectory",
            ))

        return actions
