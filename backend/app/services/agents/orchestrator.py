"""Multi-agent orchestrator.

Coordinates all SalesEdge agents, routes signals to the appropriate agents,
and manages agent lifecycle and scheduling.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import structlog

from app.services.agents.base_agent import (
    AgentContext,
    AgentResult,
    BaseAgent,
)

logger = structlog.get_logger(__name__)

# Signal type → agent name mapping
SIGNAL_ROUTING: dict[str, list[str]] = {
    "new_prospect": ["prospect_agent"],
    "prospect_enrichment": ["prospect_agent"],
    "deal_update": ["deal_intel_agent"],
    "engagement_drop": ["deal_intel_agent"],
    "competitor_mention": ["deal_intel_agent", "competitive_intel_agent"],
    "stakeholder_change": ["deal_intel_agent"],
    "churn_signal": ["retention_agent"],
    "usage_decline": ["retention_agent"],
    "support_escalation": ["retention_agent"],
    "policy_update": ["prospect_agent", "deal_intel_agent"],
    "market_signal": ["prospect_agent", "deal_intel_agent"],
}


class AgentOrchestrator:
    """Coordinates multiple agents and routes signals to them."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._run_history: list[dict[str, Any]] = []
        self._max_history = 1000

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator."""
        self._agents[agent.name] = agent
        logger.info("orchestrator.agent_registered", agent=agent.name)

    def unregister_agent(self, agent_name: str) -> None:
        """Remove an agent from the orchestrator."""
        self._agents.pop(agent_name, None)
        logger.info("orchestrator.agent_unregistered", agent=agent_name)

    async def run_all_agents(self, context: AgentContext | None = None) -> list[AgentResult]:
        """Execute all registered agents concurrently."""
        if not self._agents:
            logger.warning("orchestrator.no_agents_registered")
            return []

        ctx = context or AgentContext(triggered_by="orchestrator_full_run")
        logger.info(
            "orchestrator.run_all_start",
            run_id=ctx.run_id,
            agent_count=len(self._agents),
        )

        tasks = [
            self._execute_agent(name, agent, ctx)
            for name, agent in self._agents.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed: list[AgentResult] = []
        for r in results:
            if isinstance(r, AgentResult):
                processed.append(r)
                self._record_run(r)
            elif isinstance(r, Exception):
                logger.error("orchestrator.agent_exception", error=str(r))

        logger.info(
            "orchestrator.run_all_complete",
            run_id=ctx.run_id,
            success_count=sum(1 for r in processed if r.success),
            failure_count=sum(1 for r in processed if not r.success),
        )
        return processed

    async def route_signal(
        self,
        signal_type: str,
        payload: dict[str, Any],
        entity_id: str | None = None,
    ) -> list[AgentResult]:
        """Route a signal to the appropriate agents based on signal type."""
        target_names = SIGNAL_ROUTING.get(signal_type, [])
        if not target_names:
            logger.warning(
                "orchestrator.no_route_for_signal",
                signal_type=signal_type,
            )
            return []

        ctx = AgentContext(
            triggered_by=f"signal:{signal_type}",
            entity_id=entity_id,
            signal_payload=payload,
        )

        tasks = []
        for name in target_names:
            agent = self._agents.get(name)
            if agent:
                tasks.append(self._execute_agent(name, agent, ctx))
            else:
                logger.warning(
                    "orchestrator.agent_not_found",
                    agent=name,
                    signal_type=signal_type,
                )

        if not tasks:
            return []

        results = await asyncio.gather(*tasks, return_exceptions=True)
        processed: list[AgentResult] = []
        for r in results:
            if isinstance(r, AgentResult):
                processed.append(r)
                self._record_run(r)

        return processed

    def get_agent_status(self) -> dict[str, dict[str, Any]]:
        """Return the current status of all registered agents."""
        return {
            name: {
                "status": agent.status,
                "last_run": agent.last_run.isoformat() if agent.last_run else None,
                "run_count": agent._run_count,
                "description": agent.description,
            }
            for name, agent in self._agents.items()
        }

    def get_registered_agents(self) -> list[str]:
        return list(self._agents.keys())

    def get_run_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._run_history[-limit:]

    # ── Private helpers ──────────────────────────────────────────────────

    async def _execute_agent(
        self,
        name: str,
        agent: BaseAgent,
        context: AgentContext,
    ) -> AgentResult:
        """Execute a single agent with error isolation."""
        logger.info("orchestrator.agent_executing", agent=name, run_id=context.run_id)
        try:
            result = await agent._run_with_lifecycle(context)
            logger.info(
                "orchestrator.agent_completed",
                agent=name,
                success=result.success,
                actions=len(result.actions),
                duration_ms=result.duration_ms,
            )
            return result
        except Exception as exc:
            logger.error(
                "orchestrator.agent_error",
                agent=name,
                error=str(exc),
            )
            return AgentResult(
                agent_name=name,
                run_id=context.run_id,
                success=False,
                error=str(exc),
            )

    def _record_run(self, result: AgentResult) -> None:
        self._run_history.append({
            "agent": result.agent_name,
            "run_id": result.run_id,
            "success": result.success,
            "actions_count": len(result.actions),
            "duration_ms": result.duration_ms,
            "timestamp": result.completed_at.isoformat(),
        })
        if len(self._run_history) > self._max_history:
            self._run_history = self._run_history[-self._max_history:]
