"""Deal intelligence agent.

Monitors deal pipeline health, detects risk signals, and generates
recovery plays for at-risk deals.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog

from app.services.agents.base_agent import (
    ActionType,
    AgentAction,
    AgentContext,
    AgentResult,
    BaseAgent,
)
from app.services.scoring.deal_risk_scorer import DealData, DealRiskScorer
from app.services.scoring.recovery_prioritizer import DealWithRisk, RecoveryPrioritizer

logger = structlog.get_logger(__name__)


# Signal type constants
SIGNAL_ENGAGEMENT_DROP = "engagement_drop"
SIGNAL_COMPETITOR_MENTION = "competitor_mention"
SIGNAL_STAKEHOLDER_CHANGE = "stakeholder_change"
SIGNAL_SENTIMENT_DECLINE = "sentiment_decline"
SIGNAL_STAGE_STALL = "stage_stall"
SIGNAL_VALUE_REDUCTION = "value_reduction"


class DealIntelAgent(BaseAgent):
    """Agent that monitors deal health, detects risk, and prescribes recovery."""

    name = "deal_intel_agent"
    description = "Monitors deal risk signals and generates recovery plays"

    def __init__(
        self,
        risk_scorer: DealRiskScorer | None = None,
        prioritizer: RecoveryPrioritizer | None = None,
    ) -> None:
        self._scorer = risk_scorer or DealRiskScorer()
        self._prioritizer = prioritizer or RecoveryPrioritizer()

    async def execute(self, context: AgentContext) -> AgentResult:
        start = datetime.utcnow()
        actions: list[AgentAction] = []
        insights: list[str] = []
        metrics: dict[str, Any] = {}

        try:
            deal_id = context.entity_id
            if not deal_id:
                return AgentResult(
                    agent_name=self.name,
                    run_id=context.run_id,
                    success=False,
                    error="No entity_id (deal_id) provided",
                    duration_ms=self._elapsed_ms(start),
                )

            risk_result = await self.assess_deal_risk(deal_id, context.signal_payload)
            metrics["risk_score"] = risk_result["risk_score"]
            metrics["confidence"] = risk_result["confidence"]
            insights.append(risk_result["explanation"])

            signals = await self.detect_signals(deal_id, context.signal_payload)
            for signal in signals:
                insights.append(f"Signal detected: {signal['type']} — {signal['description']}")
            metrics["signals_detected"] = len(signals)

            risk_score = risk_result["risk_score"]
            if risk_score >= 50:
                recovery_actions = await self.generate_recovery_play(
                    deal_id, risk_score, context.signal_payload,
                )
                actions.extend(recovery_actions)
                insights.append(
                    f"Deal at risk ({risk_score}/100); "
                    f"{len(recovery_actions)} recovery actions generated"
                )

            actions.append(AgentAction(
                action_type=ActionType.UPDATE_DEAL,
                target_entity_id=deal_id,
                target_entity_type="deal",
                payload={
                    "risk_score": risk_score,
                    "risk_score_confidence": risk_result["confidence"],
                },
                priority="medium",
                rationale="Persist latest risk assessment",
            ))

            if risk_score >= 75:
                actions.append(AgentAction(
                    action_type=ActionType.ESCALATE,
                    target_entity_id=deal_id,
                    target_entity_type="deal",
                    payload={
                        "reason": f"Critical risk score: {risk_score}/100",
                        "signals": [s["type"] for s in signals],
                    },
                    priority="critical",
                    rationale="Deal risk exceeds escalation threshold",
                ))

            return AgentResult(
                agent_name=self.name,
                run_id=context.run_id,
                success=True,
                actions=actions,
                insights=insights,
                metrics=metrics,
                duration_ms=self._elapsed_ms(start),
            )
        except Exception as exc:
            logger.error("deal_intel_agent.execute_failed", error=str(exc))
            return AgentResult(
                agent_name=self.name,
                run_id=context.run_id,
                success=False,
                error=str(exc),
                duration_ms=self._elapsed_ms(start),
            )

    async def get_actions(self, context: AgentContext) -> list[AgentAction]:
        return [
            AgentAction(
                action_type=ActionType.UPDATE_DEAL,
                target_entity_type="deal",
                payload={"operation": "risk_assessment"},
                rationale="Assess deal risk and update score",
            ),
            AgentAction(
                action_type=ActionType.NOTIFY,
                target_entity_type="deal",
                payload={"operation": "signal_detection"},
                rationale="Detect and surface risk signals",
            ),
        ]

    async def assess_deal_risk(
        self,
        deal_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compute a full risk assessment for a deal."""
        payload = payload or {}
        deal_data = self._build_deal_data(deal_id, payload)
        result = self._scorer.score(deal_data)
        return {
            "deal_id": deal_id,
            "risk_score": result.risk_score,
            "confidence": result.confidence,
            "components": [
                {"name": c.name, "health": c.raw_value, "weight": c.weight}
                for c in result.components
            ],
            "explanation": result.explanation,
        }

    async def detect_signals(
        self,
        deal_id: str,
        payload: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Detect risk signals for a deal from pipeline and activity data."""
        payload = payload or {}
        signals: list[dict[str, Any]] = []

        events = payload.get("events", [])
        baseline = payload.get("baseline_event_rate", 1.0)
        window = payload.get("analysis_window_days", 14)
        if window > 0 and baseline > 0:
            rate = len(events) / window
            if rate < baseline * 0.5:
                signals.append({
                    "type": SIGNAL_ENGAGEMENT_DROP,
                    "description": f"Engagement rate ({rate:.1f}/day) is below 50% of baseline ({baseline:.1f}/day)",
                    "severity": "high",
                })

        competitor_mentions = payload.get("competitor_mentions", 0)
        if competitor_mentions > 0:
            signals.append({
                "type": SIGNAL_COMPETITOR_MENTION,
                "description": f"{competitor_mentions} competitor mention(s) detected",
                "severity": "high" if competitor_mentions > 2 else "medium",
            })

        days_in_stage = payload.get("days_in_stage", 0)
        expected_days = payload.get("expected_stage_days", 14)
        if expected_days > 0 and days_in_stage > expected_days * 1.5:
            signals.append({
                "type": SIGNAL_STAGE_STALL,
                "description": f"Deal stalled in stage for {days_in_stage} days (expected {expected_days})",
                "severity": "high" if days_in_stage > expected_days * 2 else "medium",
            })

        sentiments = payload.get("sentiment_scores", [])
        if sentiments:
            avg_sent = sum(sentiments) / len(sentiments)
            if avg_sent < -0.3:
                signals.append({
                    "type": SIGNAL_SENTIMENT_DECLINE,
                    "description": f"Average communication sentiment is negative ({avg_sent:.2f})",
                    "severity": "high" if avg_sent < -0.6 else "medium",
                })

        initial_value = payload.get("initial_value_inr")
        current_value = payload.get("value_inr")
        if initial_value and current_value and initial_value > 0:
            drift = (current_value - initial_value) / initial_value
            if drift < -0.15:
                signals.append({
                    "type": SIGNAL_VALUE_REDUCTION,
                    "description": f"Contract value drifted {drift*100:.0f}% from initial",
                    "severity": "high" if drift < -0.3 else "medium",
                })

        return signals

    async def generate_recovery_play(
        self,
        deal_id: str,
        risk_score: float,
        payload: dict[str, Any] | None = None,
    ) -> list[AgentAction]:
        """Generate recovery actions using the RecoveryPrioritizer."""
        payload = payload or {}
        deal_with_risk = DealWithRisk(
            deal_id=deal_id,
            title=payload.get("title", deal_id),
            risk_score=risk_score,
            value_inr=payload.get("value_inr", 0),
            stage=payload.get("stage", ""),
            days_in_stage=payload.get("days_in_stage", 0),
            owner=payload.get("owner"),
            champion_exists=payload.get("champion_exists", True),
            multi_threaded=payload.get("multi_threaded", False),
            engagement_events_7d=payload.get("engagement_events_7d", 0),
            competitor_mentions=payload.get("competitor_mentions", 0),
            relationship_strength=payload.get("relationship_strength", 0.5),
            executive_sponsor=payload.get("executive_sponsor", False),
        )

        prioritized = self._prioritizer.prioritize([deal_with_risk])
        actions: list[AgentAction] = []

        for pd in prioritized:
            for ra in pd.recommended_actions:
                actions.append(AgentAction(
                    action_type=ActionType.CREATE_TASK,
                    target_entity_id=deal_id,
                    target_entity_type="deal",
                    payload={
                        "action": ra.action,
                        "expected_impact": ra.expected_impact,
                    },
                    priority=ra.priority,
                    rationale=ra.rationale,
                ))

        return actions

    @staticmethod
    def _build_deal_data(deal_id: str, payload: dict[str, Any]) -> DealData:
        return DealData(
            deal_id=deal_id,
            title=payload.get("title", deal_id),
            value_inr=payload.get("value_inr", 0),
            initial_value_inr=payload.get("initial_value_inr"),
            stage=payload.get("stage", ""),
            days_in_stage=payload.get("days_in_stage", 0),
            expected_stage_days=payload.get("expected_stage_days", 14),
            events=payload.get("events", []),
            baseline_event_rate=payload.get("baseline_event_rate", 1.0),
            analysis_window_days=payload.get("analysis_window_days", 14),
            stakeholder_interactions=payload.get("stakeholder_interactions", {}),
            total_decision_makers=payload.get("total_decision_makers", 1),
            sentiment_scores=payload.get("sentiment_scores", []),
            competitor_mentions=payload.get("competitor_mentions", 0),
        )

    @staticmethod
    def _elapsed_ms(start: datetime) -> float:
        return (datetime.utcnow() - start).total_seconds() * 1000
