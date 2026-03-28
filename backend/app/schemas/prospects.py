from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProspectSummary(BaseModel):
    """Compact prospect representation for list views."""

    id: UUID
    company_name: str
    industry: str | None = None
    nic_code: str | None = None
    revenue_band_inr: str | None = Field(None, description="e.g. '10-50 Cr'")
    employee_count: int | None = None
    state: str | None = None
    fit_score: float | None = Field(None, ge=0.0, le=100.0)
    confidence: float | None = Field(None, ge=0.0, le=1.0)
    last_enriched: datetime | None = None


class FinancialHealth(BaseModel):
    """Financial health indicators for a prospect."""

    revenue_inr: float | None = None
    revenue_growth_pct: float | None = None
    profit_margin_pct: float | None = None
    debt_equity_ratio: float | None = None
    current_ratio: float | None = None
    roe_pct: float | None = None
    data_source: str | None = None
    as_of_date: datetime | None = None


class GrowthSignal(BaseModel):
    """An individual growth signal detected for a prospect."""

    signal_type: str
    description: str
    strength: str = Field(description="strong, moderate, or weak")
    detected_at: datetime
    source: str | None = None


class EnrichmentEvent(BaseModel):
    """Record of a data enrichment event."""

    source: str
    timestamp: datetime
    fields_updated: list[str]
    success: bool
    error_message: str | None = None


class Stakeholder(BaseModel):
    """Key stakeholder at a prospect company."""

    name: str
    title: str | None = None
    department: str | None = None
    linkedin_url: str | None = None
    engagement_level: str | None = Field(None, description="champion, supporter, neutral, blocker")
    last_contacted: datetime | None = None


class OutreachRecommendation(BaseModel):
    """AI-generated outreach recommendation."""

    channel: str
    timing: str
    message_theme: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str | None = None


class ProspectDetail(ProspectSummary):
    """Full prospect detail with enrichment data, financials, and recommendations."""

    city: str | None = None
    gst_number: str | None = None
    website: str | None = None
    listed_exchange: str | None = None
    bse_code: str | None = None
    nse_symbol: str | None = None
    dpiit_recognized: bool = False
    financial_health: FinancialHealth | None = None
    growth_signals: list[GrowthSignal] = Field(default_factory=list)
    enrichment_timeline: list[EnrichmentEvent] = Field(default_factory=list)
    recommended_outreach: list[OutreachRecommendation] = Field(default_factory=list)
    stakeholders: list[Stakeholder] = Field(default_factory=list)


class ProspectFilterParams(BaseModel):
    """Query parameters for prospect filtering and pagination."""

    industry: str | None = None
    state: str | None = None
    min_fit_score: float | None = Field(None, ge=0.0, le=100.0)
    max_fit_score: float | None = Field(None, ge=0.0, le=100.0)
    revenue_min_inr: float | None = None
    revenue_max_inr: float | None = None
    listed_status: str | None = Field(None, description="listed, unlisted, or all")
    sort_by: str = "fit_score"
    sort_order: str = "desc"
    page: int = Field(1, ge=1)
    page_size: int = Field(25, ge=1, le=100)
