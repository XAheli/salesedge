"""Retention agent.

Predicts churn, monitors customer health signals, and triggers
intervention workflows for at-risk accounts.
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
from app.services.scoring.churn_predictor import ChurnPredictor, CustomerData

logger = structlog.get_logger(__name__)

# Intervention playbook keyed by risk level
INTERVENTION_PLAYBOOK: dict[str, list[dict[str, str]]] = {
    "critical": [
        {
            "type": "executive_outreach",
            "description": "Schedule executive-to-executive meeting within 48 hours",
        },
        {
            "type": "qbr",
            "description": "Fast-track a Quarterly Business Review to discuss value realisation",
        },
        {
            "type": "escalation",
            "description": "Escalate to VP of Customer Success for immediate attention",
        },
    ],
    "high": [
        {
            "type": "qbr",
            "description": "Schedule an ad-hoc business review to address declining health signals",
        },
        {
            "type": "training",
            "description": "Offer adoption workshop targeting underused features",
        },
    ],
    "medium": [
        {
            "type": "feature_unlock",
            "description": "Consider unlocking premium features to demonstrate incremental value",
        },
        {
            "type": "training",
            "description": "Send curated training materials based on usage patterns",
        },
    ],
    "low": [
        {
            "type": "nurture",
            "description": "Continue standard health-check cadence; no immediate intervention needed",
        },
    ],
}


class RetentionAgent(BaseAgent):
    """Agent that monitors customer health, predicts churn, and triggers interventions."""

    name = "retention_agent"
    description = "Predicts churn and orchestrates retention interventions"

    def __init__(self, predictor: ChurnPredictor | None = None) -> None:
        self._predictor = predictor or ChurnPredictor()

    async def execute(self, context: AgentContext) -> AgentResult:
        start = datetime.utcnow()
        actions: list[AgentAction] = []
        insights: list[str] = []
        metrics: dict[str, Any] = {}

        try:
            customer_id = context.entity_id
            if not customer_id:
                return AgentResult(
                    agent_name=self.name,
                    run_id=context.run_id,
                    success=False,
                    error="No entity_id (customer_id) provided",
                    duration_ms=self._elapsed_ms(start),
                )

            prediction = await self.predict_churn(customer_id, context.signal_payload)
            metrics["churn_probability"] = prediction.probability
            metrics["risk_level"] = prediction.risk_level
            insights.append(
                f"Churn probability: {prediction.probability:.1%} ({prediction.risk_level})"
            )

            if prediction.contributing_factors:
                top_factors = prediction.contributing_factors[:3]
                insights.append(
                    "Top risk factors: "
                    + ", ".join(f"{f} ({v:+.3f})" for f, v in top_factors)
                )

            intervention_actions = await self.suggest_intervention(
                customer_id, prediction.risk_level, prediction.probability,
            )
            actions.extend(intervention_actions)
            metrics["interventions_suggested"] = len(intervention_actions)

            actions.append(AgentAction(
                action_type=ActionType.UPDATE_RECORD,
                target_entity_id=customer_id,
                target_entity_type="customer",
                payload={
                    "churn_probability": prediction.probability,
                    "churn_risk_level": prediction.risk_level,
                    "churn_predicted_at": datetime.utcnow().isoformat(),
                },
                priority="medium",
                rationale="Persist churn prediction to customer record",
            ))

            if prediction.risk_level in ("critical", "high"):
                actions.append(AgentAction(
                    action_type=ActionType.NOTIFY,
                    payload={
                        "customer_id": customer_id,
                        "churn_probability": prediction.probability,
                        "risk_level": prediction.risk_level,
                        "message": (
                            f"Customer {customer_id} flagged as {prediction.risk_level} "
                            f"churn risk ({prediction.probability:.0%})"
                        ),
                    },
                    priority="high" if prediction.risk_level == "critical" else "medium",
                    rationale="Alert CSM about at-risk account",
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
            logger.error("retention_agent.execute_failed", error=str(exc))
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
                action_type=ActionType.UPDATE_RECORD,
                target_entity_type="customer",
                payload={"operation": "churn_prediction"},
                rationale="Run churn prediction for the customer",
            ),
            AgentAction(
                action_type=ActionType.CREATE_TASK,
                target_entity_type="customer",
                payload={"operation": "intervention"},
                rationale="Create intervention tasks based on risk level",
            ),
        ]

    async def predict_churn(
        self,
        customer_id: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """Run the churn predictor for a single customer."""
        payload = payload or {}
        customer = CustomerData(
            customer_id=customer_id,
            company_name=payload.get("company_name", customer_id),
            usage_trend_30d=payload.get("usage_trend_30d", 0.0),
            support_ticket_frequency=payload.get("support_ticket_frequency", 0.0),
            nps_score=payload.get("nps_score", 0.0),
            payment_delays=payload.get("payment_delays", 0.0),
            champion_turnover=payload.get("champion_turnover", 0.0),
            competitive_mentions=payload.get("competitive_mentions", 0.0),
            contract_renewal_proximity=payload.get("contract_renewal_proximity", 0.0),
            macro_headwind=payload.get("macro_headwind", 0.0),
        )
        return self._predictor.predict(customer)

    async def suggest_intervention(
        self,
        customer_id: str,
        risk_level: str,
        churn_probability: float,
    ) -> list[AgentAction]:
        """Select intervention actions from the playbook based on risk level."""
        interventions = INTERVENTION_PLAYBOOK.get(risk_level, [])
        actions: list[AgentAction] = []

        for iv in interventions:
            action_type = (
                ActionType.ESCALATE
                if iv["type"] == "escalation"
                else ActionType.CREATE_TASK
            )
            actions.append(AgentAction(
                action_type=action_type,
                target_entity_id=customer_id,
                target_entity_type="customer",
                payload={
                    "intervention_type": iv["type"],
                    "description": iv["description"],
                    "churn_probability": churn_probability,
                },
                priority="critical" if risk_level == "critical" else "high",
                rationale=iv["description"],
            ))

        return actions

    @staticmethod
    def _elapsed_ms(start: datetime) -> float:
        return (datetime.utcnow() - start).total_seconds() * 1000
