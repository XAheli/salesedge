from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CompetitiveMention(BaseModel):
    """A competitive intelligence mention sourced from signals or deal notes."""

    id: UUID
    competitor_name: str
    source: str = Field(description="deal_note, news, earnings_call, social, job_posting")
    snippet: str
    sentiment: str = Field(description="positive, neutral, or negative")
    deal_id: UUID | None = None
    deal_name: str | None = None
    detected_at: datetime
    url: str | None = None


class BattlecardSection(BaseModel):
    """A section within a competitive battlecard."""

    heading: str
    content: str
    last_updated: datetime


class Battlecard(BaseModel):
    """Competitive battlecard for a specific competitor."""

    competitor_name: str
    logo_url: str | None = None
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    differentiators: list[str]
    common_objections: list[str]
    counter_arguments: list[str]
    pricing_comparison: str | None = None
    win_rate_against: float | None = Field(None, ge=0.0, le=100.0)
    total_encounters: int = 0
    sections: list[BattlecardSection] = Field(default_factory=list)
    last_updated: datetime


class PolicySignal(BaseModel):
    """Government policy or regulatory signal relevant to sales territory."""

    id: UUID
    title: str
    summary: str
    policy_body: str = Field(description="e.g. 'RBI', 'SEBI', 'MCA', 'DPIIT'")
    impact_assessment: str = Field(description="positive, neutral, negative, or mixed")
    affected_industries: list[str]
    affected_states: list[str] = Field(default_factory=list)
    source_url: str | None = None
    published_at: datetime
    detected_at: datetime


class MarketSignal(BaseModel):
    """Macro-level market signal or trend."""

    id: UUID
    title: str
    summary: str
    signal_type: str = Field(
        description="sector_trend, funding_round, ipo, m_and_a, earnings, macro_indicator"
    )
    impact_score: float = Field(ge=0.0, le=10.0)
    affected_sectors: list[str]
    data_points: dict | None = Field(None, description="Supporting numerical data")
    source: str
    source_url: str | None = None
    published_at: datetime
