"""Prospecting agent.

Researches prospects using government data and market sources, scores them
for ICP fit, and generates outreach recommendations.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
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
from app.services.scoring.prospect_scorer import ProspectData, ProspectScorer

logger = structlog.get_logger(__name__)


@dataclass
class ProspectResearchResult:
    """Aggregated research data from multiple sources."""

    company_name: str
    sources_consulted: list[str] = field(default_factory=list)
    mca_data: dict[str, Any] | None = None
    gst_data: dict[str, Any] | None = None
    market_data: dict[str, Any] | None = None
    news_mentions: list[dict[str, Any]] = field(default_factory=list)
    enrichment_fields: dict[str, Any] = field(default_factory=dict)
    research_timestamp: datetime = field(default_factory=datetime.utcnow)


class ProspectAgent(BaseAgent):
    """Autonomous agent that researches, scores, and recommends outreach for prospects."""

    name = "prospect_agent"
    description = "Researches and scores new prospects for ICP fit"

    def __init__(self, scorer: ProspectScorer | None = None) -> None:
        self._scorer = scorer or ProspectScorer()

    async def execute(self, context: AgentContext) -> AgentResult:
        start = datetime.utcnow()
        actions: list[AgentAction] = []
        insights: list[str] = []
        metrics: dict[str, Any] = {}

        try:
            company_name = context.signal_payload.get("company_name", "")
            if not company_name and context.entity_id:
                company_name = context.entity_id

            if not company_name:
                return AgentResult(
                    agent_name=self.name,
                    run_id=context.run_id,
                    success=False,
                    error="No company_name or entity_id provided",
                    duration_ms=self._elapsed_ms(start),
                )

            research = await self.research_prospect(company_name)
            insights.append(
                f"Consulted {len(research.sources_consulted)} sources for {company_name}"
            )

            prospect_data = self._build_prospect_data(company_name, research)
            scoring_result = self._scorer.score(prospect_data)
            metrics["fit_score"] = scoring_result.score
            metrics["confidence"] = scoring_result.confidence
            insights.append(scoring_result.explanation)

            if scoring_result.score >= 60:
                outreach_actions = await self.generate_outreach(
                    company_name, scoring_result.score, research,
                )
                actions.extend(outreach_actions)
                insights.append(
                    f"High-fit prospect ({scoring_result.score}); "
                    f"{len(outreach_actions)} outreach actions queued"
                )

            actions.append(AgentAction(
                action_type=ActionType.UPDATE_RECORD,
                target_entity_id=context.entity_id,
                target_entity_type="prospect",
                payload={
                    "fit_score": scoring_result.score,
                    "fit_score_confidence": scoring_result.confidence,
                    "last_enriched_at": datetime.utcnow().isoformat(),
                },
                priority="medium",
                rationale="Update prospect record with latest scoring",
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
            logger.error("prospect_agent.execute_failed", error=str(exc))
            return AgentResult(
                agent_name=self.name,
                run_id=context.run_id,
                success=False,
                error=str(exc),
                duration_ms=self._elapsed_ms(start),
            )

    async def get_actions(self, context: AgentContext) -> list[AgentAction]:
        actions = [
            AgentAction(
                action_type=ActionType.UPDATE_RECORD,
                target_entity_type="prospect",
                payload={"operation": "research_and_score"},
                rationale="Research prospect and compute fit score",
            ),
        ]
        company_name = context.signal_payload.get("company_name", "")
        if company_name:
            actions.append(AgentAction(
                action_type=ActionType.TRIGGER_OUTREACH,
                target_entity_type="prospect",
                payload={"company_name": company_name},
                rationale="Generate outreach if fit score is sufficient",
            ))
        return actions

    async def research_prospect(self, company_name: str) -> ProspectResearchResult:
        """Gather data from government and market sources for a company.

        In production this calls MCA, GST, BSE/NSE, and OGD connectors.
        """
        logger.info("prospect_agent.researching", company=company_name)

        mca_task = self._fetch_mca_data(company_name)
        gst_task = self._fetch_gst_data(company_name)
        market_task = self._fetch_market_data(company_name)

        mca_data, gst_data, market_data = await asyncio.gather(
            mca_task, gst_task, market_task, return_exceptions=True,
        )

        sources: list[str] = []
        result = ProspectResearchResult(company_name=company_name)

        if not isinstance(mca_data, Exception) and mca_data:
            result.mca_data = mca_data
            sources.append("mca")
        if not isinstance(gst_data, Exception) and gst_data:
            result.gst_data = gst_data
            sources.append("gst")
        if not isinstance(market_data, Exception) and market_data:
            result.market_data = market_data
            sources.append("market")

        result.sources_consulted = sources
        return result

    async def enrich_prospect(self, prospect_id: str) -> dict[str, Any]:
        """Pull fresh enrichment data for an already-tracked prospect."""
        logger.info("prospect_agent.enriching", prospect_id=prospect_id)
        research = await self.research_prospect(prospect_id)
        return research.enrichment_fields

    async def generate_outreach(
        self,
        company_name: str,
        fit_score: float,
        research: ProspectResearchResult,
    ) -> list[AgentAction]:
        """Generate outreach actions based on fit score and research context."""
        actions: list[AgentAction] = []

        if fit_score >= 80:
            actions.append(AgentAction(
                action_type=ActionType.TRIGGER_OUTREACH,
                payload={
                    "company_name": company_name,
                    "channel": "email",
                    "template": "high_fit_intro",
                    "personalisation": {
                        "industry": research.market_data.get("industry") if research.market_data else None,
                    },
                },
                priority="high",
                rationale=f"Exceptional fit score ({fit_score}); prioritise outreach",
            ))
            actions.append(AgentAction(
                action_type=ActionType.TRIGGER_OUTREACH,
                payload={
                    "company_name": company_name,
                    "channel": "linkedin",
                    "template": "connection_request",
                },
                priority="medium",
                rationale="Multi-channel approach for high-fit prospects",
            ))
        elif fit_score >= 60:
            actions.append(AgentAction(
                action_type=ActionType.TRIGGER_OUTREACH,
                payload={
                    "company_name": company_name,
                    "channel": "email",
                    "template": "moderate_fit_intro",
                },
                priority="medium",
                rationale=f"Good fit score ({fit_score}); standard outreach",
            ))

        if actions:
            actions.append(AgentAction(
                action_type=ActionType.CREATE_TASK,
                payload={
                    "title": f"Follow up with {company_name}",
                    "due_in_days": 3,
                },
                priority="medium",
                rationale="Schedule follow-up after initial outreach",
            ))

        return actions

    # ── Data source stubs (replaced by real connectors in production) ────

    async def _fetch_mca_data(self, company_name: str) -> dict[str, Any] | None:
        try:
            from app.connectors.government.mca import MCAConnector

            connector = MCAConnector()
            return await connector.search_company(company_name)
        except Exception as exc:
            logger.warning(
                "prospect_agent.mca_fetch_failed",
                company=company_name,
                error=str(exc),
            )
            return None

    async def _fetch_gst_data(self, company_name: str) -> dict[str, Any] | None:
        logger.warning(
            "prospect_agent.gst_stub_unconnected",
            company=company_name,
            hint="No GST connector available yet; wire one when the API is accessible",
        )
        return None

    async def _fetch_market_data(self, company_name: str) -> dict[str, Any] | None:
        try:
            from app.connectors.market.bse import BSEConnector

            connector = BSEConnector()
            logger.warning(
                "prospect_agent.market_data_limited",
                company=company_name,
                hint="BSE connector requires a scrip code, not a company name; returning None",
            )
            return None
        except Exception as exc:
            logger.warning(
                "prospect_agent.market_fetch_failed",
                company=company_name,
                error=str(exc),
            )
            return None

    @staticmethod
    def _build_prospect_data(
        company_name: str,
        research: ProspectResearchResult,
    ) -> ProspectData:
        """Merge research results into a ProspectData instance."""
        data = ProspectData(company_name=company_name)
        if research.mca_data:
            data.mca_registration_date = research.mca_data.get("registration_date")
            data.nic_code = research.mca_data.get("nic_code")
            data.state = research.mca_data.get("state")
        if research.gst_data:
            data.gst_filing_frequency = research.gst_data.get("filing_frequency")
        if research.market_data:
            data.revenue_inr = research.market_data.get("revenue_inr")
            data.industry = research.market_data.get("industry")
            data.employee_count = research.market_data.get("employee_count")
            data.listed_exchange = research.market_data.get("listed_exchange")
        return data

    @staticmethod
    def _elapsed_ms(start: datetime) -> float:
        return (datetime.utcnow() - start).total_seconds() * 1000
