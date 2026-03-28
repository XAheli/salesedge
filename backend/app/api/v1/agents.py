"""Agent management and execution API endpoints.

These endpoints allow users to:
- View agent status and configuration
- Trigger agent runs manually
- Chat with agents for analysis
- View agent run history
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.schemas.common import APIResponse, ResponseMetadata
from app.services.llm.client import get_llm_client
from app.services.llm.prompts import (
    BATTLECARD_PROMPT,
    CHURN_ANALYSIS_PROMPT,
    DEAL_RISK_PROMPT,
    OUTREACH_GENERATION_PROMPT,
    PROSPECT_ANALYSIS_PROMPT,
    SYSTEM_PROMPTS,
)

router = APIRouter(prefix="/agents", tags=["agents"])


# ── Request / response models ───────────────────────────────────


class AgentChatRequest(BaseModel):
    agent: str  # "prospect", "deal_intel", "retention", "competitive"
    message: str
    context: dict[str, Any] = {}


class AgentChatResponse(BaseModel):
    agent: str
    response: str
    model_used: str
    is_configured: bool


class AgentStatus(BaseModel):
    name: str
    status: str
    description: str
    is_llm_configured: bool
    last_run: str | None = None
    run_count: int = 0
    supported_actions: list[str] = []


class ProspectAnalysisRequest(BaseModel):
    company_name: str
    industry: str = ""
    revenue_cr: float = 0
    employee_count: int = 0
    state: str = ""
    listed_exchange: str = "unlisted"
    additional_context: str = ""


class DealRiskRequest(BaseModel):
    deal_title: str
    company_name: str
    value_lakhs: float
    stage: str
    days_in_stage: int = 0
    expected_close: str = ""
    engagement_summary: str = ""
    stakeholder_summary: str = ""
    competitor_mentions: str = ""


class OutreachRequest(BaseModel):
    company_name: str
    industry: str = ""
    company_size: str = ""
    contact_name: str = ""
    contact_title: str = ""
    fit_score: int = 0
    channel: str = "email"


# ── Endpoints ────────────────────────────────────────────────────


@router.get("/status")
async def get_agents_status() -> APIResponse[list[AgentStatus]]:
    """Get status of all AI agents and whether LLM is configured."""
    llm = get_llm_client()
    agents = [
        AgentStatus(
            name="prospect_agent",
            status="ready" if llm.is_configured else "needs_config",
            description="Researches, scores, and recommends outreach for prospects",
            is_llm_configured=llm.is_configured,
            supported_actions=["research", "score", "generate_outreach", "chat"],
        ),
        AgentStatus(
            name="deal_intel_agent",
            status="ready" if llm.is_configured else "needs_config",
            description="Monitors deal health, detects risk signals, suggests recovery plays",
            is_llm_configured=llm.is_configured,
            supported_actions=["assess_risk", "detect_signals", "recovery_play", "chat"],
        ),
        AgentStatus(
            name="retention_agent",
            status="ready" if llm.is_configured else "needs_config",
            description="Predicts churn, monitors customer health, triggers interventions",
            is_llm_configured=llm.is_configured,
            supported_actions=["predict_churn", "suggest_intervention", "chat"],
        ),
        AgentStatus(
            name="competitive_agent",
            status="ready" if llm.is_configured else "needs_config",
            description="Tracks competitors, generates battlecards, monitors market signals",
            is_llm_configured=llm.is_configured,
            supported_actions=["track_mentions", "generate_battlecard", "chat"],
        ),
    ]
    return APIResponse(
        success=True,
        data=agents,
        meta=ResponseMetadata(),
    )


@router.post("/chat")
async def agent_chat(req: AgentChatRequest) -> APIResponse[AgentChatResponse]:
    """Chat with any agent for analysis. Works with OpenRouter, OpenAI, or Ollama."""
    llm = get_llm_client()

    agent_key = f"{req.agent}_agent"
    system_prompt = SYSTEM_PROMPTS.get(agent_key)
    if not system_prompt:
        raise HTTPException(
            404,
            f"Agent '{req.agent}' not found. "
            "Available: prospect, deal_intel, retention, competitive",
        )

    response = await llm.complete(
        prompt=req.message,
        system_prompt=system_prompt,
    )

    return APIResponse(
        success=True,
        data=AgentChatResponse(
            agent=req.agent,
            response=response,
            model_used=llm.model,
            is_configured=llm.is_configured,
        ),
        meta=ResponseMetadata(),
    )


@router.post("/prospect/analyze")
async def analyze_prospect(req: ProspectAnalysisRequest) -> APIResponse[dict]:
    """AI-powered prospect analysis using government and market data context."""
    llm = get_llm_client()
    prompt = PROSPECT_ANALYSIS_PROMPT.format(
        company_name=req.company_name,
        industry=req.industry,
        revenue_cr=req.revenue_cr,
        employee_count=req.employee_count,
        state=req.state,
        listed_exchange=req.listed_exchange,
        mca_date="N/A",
        gst_status="Registered" if req.revenue_cr > 0 else "Unknown",
        additional_context=req.additional_context,
    )
    result = await llm.complete_json(prompt, system_prompt=SYSTEM_PROMPTS["prospect_agent"])
    return APIResponse(
        success=True,
        data=result if isinstance(result, dict) else result.model_dump(),
        meta=ResponseMetadata(),
    )


@router.post("/deal/risk-analysis")
async def analyze_deal_risk(req: DealRiskRequest) -> APIResponse[dict]:
    """AI-powered deal risk analysis."""
    llm = get_llm_client()
    prompt = DEAL_RISK_PROMPT.format(**req.model_dump())
    result = await llm.complete_json(
        prompt, system_prompt=SYSTEM_PROMPTS["deal_intel_agent"]
    )
    return APIResponse(
        success=True,
        data=result if isinstance(result, dict) else result.model_dump(),
        meta=ResponseMetadata(),
    )


@router.post("/outreach/generate")
async def generate_outreach(req: OutreachRequest) -> APIResponse[dict]:
    """AI-generated personalized outreach message."""
    llm = get_llm_client()
    prompt = OUTREACH_GENERATION_PROMPT.format(
        company_name=req.company_name,
        industry=req.industry,
        company_size=req.company_size,
        contact_name=req.contact_name,
        contact_title=req.contact_title,
        fit_score=req.fit_score,
        value_props="Revenue operations intelligence, government data integration, deal risk prediction",
        indian_context=f"Based in India, {req.industry} sector",
        channel=req.channel,
    )
    result = await llm.complete_json(
        prompt, system_prompt=SYSTEM_PROMPTS["prospect_agent"]
    )
    return APIResponse(
        success=True,
        data=result if isinstance(result, dict) else result.model_dump(),
        meta=ResponseMetadata(),
    )


@router.post("/battlecard/generate")
async def generate_battlecard(
    competitor_name: str = "Salesforce",
    deal_context: str = "",
    industry: str = "",
) -> APIResponse[dict]:
    """Generate AI-powered competitive battlecard."""
    llm = get_llm_client()
    prompt = BATTLECARD_PROMPT.format(
        competitor_name=competitor_name,
        deal_context=deal_context or "Enterprise B2B deal in India",
        industry=industry or "Technology",
        company_size="Enterprise",
        competitor_strengths="Market leader, brand recognition, ecosystem",
        competitor_weaknesses="Expensive, complex, less India-focused",
        competitor_news="",
    )
    result = await llm.complete_json(
        prompt, system_prompt=SYSTEM_PROMPTS["competitive_agent"]
    )
    return APIResponse(
        success=True,
        data=result if isinstance(result, dict) else result.model_dump(),
        meta=ResponseMetadata(),
    )
