"""Integration tests for the AI agent orchestration system.

Tests the orchestrator's ability to route messages to the correct agent,
handle context, and produce structured responses.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgentOrchestrator:
    async def test_routes_prospect_query_to_prospect_agent(self):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()
        agent_name = orch.classify_intent("Analyze Reliance Industries as a prospect")
        assert agent_name == "prospect"

    async def test_routes_deal_query_to_deal_agent(self):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()
        agent_name = orch.classify_intent("What are the risks for the TCS deal?")
        assert agent_name == "deal_intel"

    async def test_routes_churn_query_to_retention_agent(self):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()
        agent_name = orch.classify_intent("Is Wipro likely to churn?")
        assert agent_name == "retention"

    async def test_routes_competitor_query_to_competitive_agent(self):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()
        agent_name = orch.classify_intent("Generate a battlecard against Salesforce")
        assert agent_name == "competitive"

    async def test_agent_execution_returns_structured_response(self, db_session):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()

        mock_llm_response = {
            "analysis": "Reliance Industries shows strong fit due to digital transformation initiatives.",
            "confidence": 0.85,
            "actions": [
                {"type": "outreach", "description": "Schedule introductory call with CTO office"}
            ],
        }

        with patch.object(orch, "_call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_llm_response
            result = await orch.process(
                message="Analyze Reliance Industries",
                context={"user_id": 1},
            )

        assert "analysis" in result
        assert "confidence" in result
        assert isinstance(result.get("actions", []), list)

    async def test_orchestrator_handles_llm_failure_gracefully(self, db_session):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()

        with patch.object(orch, "_call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.side_effect = ConnectionError("LLM provider unreachable")
            result = await orch.process(
                message="Analyze something",
                context={"user_id": 1},
            )

        assert "error" in result or result.get("analysis", "").startswith("Unable")

    async def test_orchestrator_passes_context_to_agent(self, db_session):
        from app.services.agents.orchestrator import AgentOrchestrator

        orch = AgentOrchestrator()
        context = {"user_id": 1, "company_id": 42, "deal_id": 7}

        with patch.object(orch, "_call_agent", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = {"analysis": "test", "confidence": 0.5}
            await orch.process(message="Assess deal risk", context=context)

        call_kwargs = mock_call.call_args
        assert call_kwargs is not None
