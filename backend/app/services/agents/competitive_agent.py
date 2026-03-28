"""Competitive intelligence agent.

Tracks competitor mentions across deal signals, news, and other sources,
and maintains up-to-date battlecards.
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

logger = structlog.get_logger(__name__)

# Known competitor profiles for battlecard generation
DEFAULT_COMPETITOR_PROFILES: dict[str, dict[str, Any]] = {
    "competitor_a": {
        "display_name": "Competitor A",
        "known_strengths": ["Strong brand recognition", "Large enterprise footprint"],
        "known_weaknesses": ["Slow product iteration", "Limited India-specific features"],
    },
}


class CompetitiveIntelAgent(BaseAgent):
    """Agent that tracks competitors and maintains battlecards."""

    name = "competitive_intel_agent"
    description = "Tracks competitor signals and generates battlecards"

    def __init__(
        self,
        competitor_profiles: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self._profiles = competitor_profiles or DEFAULT_COMPETITOR_PROFILES.copy()

    async def execute(self, context: AgentContext) -> AgentResult:
        start = datetime.utcnow()
        actions: list[AgentAction] = []
        insights: list[str] = []
        metrics: dict[str, Any] = {}

        try:
            deal_id = context.entity_id
            competitor_name = context.signal_payload.get("competitor_name")

            if deal_id:
                mentions = await self.track_competitors(deal_id, context.signal_payload)
                metrics["mentions_found"] = len(mentions)
                for m in mentions:
                    insights.append(
                        f"Competitor {m['competitor']} mentioned in {m['source']}: "
                        f"{m['snippet'][:80]}"
                    )

                if mentions:
                    actions.append(AgentAction(
                        action_type=ActionType.NOTIFY,
                        target_entity_id=deal_id,
                        target_entity_type="deal",
                        payload={
                            "type": "competitor_alert",
                            "mentions": mentions,
                        },
                        priority="high" if len(mentions) > 2 else "medium",
                        rationale=f"{len(mentions)} competitor mention(s) detected in deal",
                    ))

            if competitor_name:
                battlecard = await self.update_battlecard(
                    competitor_name, context.signal_payload,
                )
                metrics["battlecard_sections"] = len(battlecard.get("sections", []))
                insights.append(
                    f"Battlecard for {competitor_name} updated with "
                    f"{metrics['battlecard_sections']} sections"
                )

                actions.append(AgentAction(
                    action_type=ActionType.UPDATE_RECORD,
                    target_entity_type="battlecard",
                    payload=battlecard,
                    priority="medium",
                    rationale=f"Persist updated battlecard for {competitor_name}",
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
            logger.error("competitive_agent.execute_failed", error=str(exc))
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
                action_type=ActionType.NOTIFY,
                target_entity_type="deal",
                payload={"operation": "track_competitors"},
                rationale="Scan for competitor mentions across signals",
            ),
            AgentAction(
                action_type=ActionType.UPDATE_RECORD,
                target_entity_type="battlecard",
                payload={"operation": "update_battlecard"},
                rationale="Refresh competitive battlecard content",
            ),
        ]

    async def track_competitors(
        self,
        deal_id: str,
        payload: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Scan deal signals and notes for competitor mentions.

        In production this queries the signal store and NLP pipeline.
        """
        payload = payload or {}
        mentions: list[dict[str, Any]] = []

        raw_mentions = payload.get("competitor_mentions_raw", [])
        for raw in raw_mentions:
            mentions.append({
                "competitor": raw.get("name", "unknown"),
                "source": raw.get("source", "deal_note"),
                "snippet": raw.get("snippet", ""),
                "sentiment": raw.get("sentiment", "neutral"),
                "detected_at": datetime.utcnow().isoformat(),
                "deal_id": deal_id,
            })

        deal_notes = payload.get("deal_notes", [])
        known = set(self._profiles.keys())
        for note in deal_notes:
            text_lower = note.get("text", "").lower()
            for comp_key in known:
                display = self._profiles[comp_key].get("display_name", comp_key)
                if comp_key in text_lower or display.lower() in text_lower:
                    mentions.append({
                        "competitor": display,
                        "source": "deal_note",
                        "snippet": note.get("text", "")[:200],
                        "sentiment": "neutral",
                        "detected_at": datetime.utcnow().isoformat(),
                        "deal_id": deal_id,
                    })

        return mentions

    async def update_battlecard(
        self,
        competitor_name: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate or refresh a battlecard for a competitor.

        In production this aggregates signals, win/loss data, and LLM-generated
        positioning content.
        """
        payload = payload or {}
        key = competitor_name.lower().replace(" ", "_")
        profile = self._profiles.get(key, {})
        our_product = payload.get("our_product_name", "SalesEdge")
        deal_context = payload.get("deal_context", {})

        strengths_theirs = profile.get("known_strengths", [])
        weaknesses_theirs = profile.get("known_weaknesses", [])

        sections = [
            {
                "heading": "Overview",
                "content": (
                    f"{competitor_name} is a competitor encountered in "
                    f"{deal_context.get('deal_count', 'multiple')} deals."
                ),
            },
            {
                "heading": "Their Strengths",
                "content": "; ".join(strengths_theirs) if strengths_theirs else "Under research",
            },
            {
                "heading": "Our Strengths",
                "content": (
                    f"{our_product} differentiates with India-first data integration, "
                    "real-time government data signals, and multi-agent AI pipeline."
                ),
            },
            {
                "heading": "Their Weaknesses",
                "content": "; ".join(weaknesses_theirs) if weaknesses_theirs else "Under research",
            },
            {
                "heading": "Positioning",
                "content": (
                    f"Position {our_product} as the only solution with native OGD, MCA, "
                    "and SEBI integration for India-centric sales intelligence."
                ),
            },
            {
                "heading": "Objection Handling",
                "content": payload.get("objection_notes", "Standard objection playbook applies."),
            },
            {
                "heading": "Pricing Comparison",
                "content": payload.get("pricing_notes", "Pricing intelligence pending."),
            },
        ]

        return {
            "competitor_name": competitor_name,
            "summary": f"Competitive battlecard for {competitor_name} vs {our_product}",
            "strengths_theirs": strengths_theirs,
            "weaknesses_theirs": weaknesses_theirs,
            "sections": sections,
            "win_rate_against": payload.get("win_rate", None),
            "total_encounters": payload.get("encounter_count", 0),
            "last_updated": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _elapsed_ms(start: datetime) -> float:
        return (datetime.utcnow() - start).total_seconds() * 1000
