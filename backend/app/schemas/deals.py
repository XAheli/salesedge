from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DealSummary(BaseModel):
    """Compact deal representation for list views."""

    id: UUID
    prospect_name: str
    stage: str
    value_inr: float
    risk_score: float = Field(ge=0.0, le=100.0)
    days_in_stage: int
    owner: str | None = None
    last_activity: datetime | None = None


class DealRiskFactors(BaseModel):
    """Individual risk factor breakdown for a deal."""

    engagement_momentum: float = Field(ge=0.0, le=1.0, description="Recent engagement velocity")
    stakeholder_coverage: float = Field(
        ge=0.0, le=1.0, description="Fraction of key stakeholders engaged"
    )
    stage_velocity: float = Field(
        ge=0.0, le=1.0, description="Speed vs. historical avg for this stage"
    )
    sentiment_trend: float = Field(
        ge=-1.0, le=1.0, description="Positive (1) to negative (-1)"
    )
    competitor_presence: float = Field(
        ge=0.0, le=1.0, description="Strength of competitor involvement"
    )
    contract_value_drift: float = Field(
        ge=-1.0, le=1.0, description="Change from initial quoted value"
    )


class EngagementEvent(BaseModel):
    """Logged engagement event on a deal."""

    event_type: str
    timestamp: datetime
    description: str
    sentiment: str | None = Field(None, description="positive, neutral, or negative")
    actor: str | None = None


class RecoveryPlay(BaseModel):
    """AI-recommended recovery action for an at-risk deal."""

    action: str
    priority: str = Field(description="critical, high, medium, low")
    rationale: str
    expected_impact: str
    suggested_owner: str | None = None
    deadline: datetime | None = None


class CompetitorMention(BaseModel):
    """A detected competitor mention within a deal context."""

    competitor_name: str
    source: str
    snippet: str
    sentiment: str | None = None
    detected_at: datetime


class StakeholderCoverage(BaseModel):
    """Stakeholder coverage summary for a deal."""

    total_identified: int
    engaged: int
    champions: int
    blockers: int
    neutral: int
    coverage_pct: float = Field(ge=0.0, le=100.0)


class DealDetail(DealSummary):
    """Full deal detail with risk analysis, engagement history, and recovery plays."""

    expected_close_date: datetime | None = None
    win_probability: float | None = Field(None, ge=0.0, le=1.0)
    engagement_score: float | None = Field(None, ge=0.0, le=100.0)
    risk_factors: DealRiskFactors | None = None
    engagement_history: list[EngagementEvent] = Field(default_factory=list)
    stakeholder_coverage: StakeholderCoverage | None = None
    competitor_mentions: list[CompetitorMention] = Field(default_factory=list)
    recovery_plays: list[RecoveryPlay] = Field(default_factory=list)
