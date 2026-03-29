from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KPIMetric(BaseModel):
    """A single KPI metric with trend information and provenance."""

    value: float
    formatted: str
    trend_pct: float = Field(description="Percentage change from prior period")
    trend_direction: str = Field(description="up, down, or flat")
    is_positive: bool = Field(description="Whether the trend is favourable")
    sparkline: list[float] = Field(
        default_factory=list, description="Last N period values for inline chart"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    source: str | None = None
    last_updated: datetime | None = None


class ExecutiveKPIs(BaseModel):
    """Top-line KPIs for the executive dashboard."""

    arr: KPIMetric
    mrr: KPIMetric
    pipeline_value: KPIMetric
    win_rate: KPIMetric
    avg_deal_cycle: KPIMetric
    net_revenue_retention: KPIMetric


class RevenueForecast(BaseModel):
    """Revenue forecast with confidence intervals."""

    period: str
    forecast_value: float
    lower_bound: float
    upper_bound: float
    confidence_level: float
    model_version: str | None = None


class PipelineVelocityData(BaseModel):
    """Pipeline velocity metrics per stage."""

    stage: str
    deal_count: int
    avg_value_inr: float
    avg_days_in_stage: float
    conversion_rate: float
    velocity_trend: str


class FunnelStage(BaseModel):
    """A single stage in the sales funnel."""

    stage_name: str
    count: int
    value_inr: float
    conversion_rate: float


class FunnelData(BaseModel):
    """Full sales funnel with stage-by-stage breakdown."""

    stages: list[FunnelStage]
    overall_conversion: float
    period: str


class RiskHeatmapCell(BaseModel):
    """Single cell in the deal risk heatmap."""

    segment: str
    risk_level: str
    deal_count: int
    total_value_inr: float


class RiskHeatmapData(BaseModel):
    """Risk heatmap across segments and risk levels."""

    cells: list[RiskHeatmapCell]
    risk_levels: list[str] = Field(default=["low", "medium", "high", "critical"])


class DealSummary(BaseModel):
    """Compact deal representation for dashboard widgets."""

    id: UUID
    prospect_name: str
    stage: str
    value_inr: float
    risk_score: float
    days_in_stage: int
    owner: str | None = None


class ExecutiveSummary(BaseModel):
    """Combined executive dashboard payload."""

    kpis: ExecutiveKPIs
    revenue_forecast: dict | list = []
    pipeline_velocity: list[dict] | list = []
    funnel: FunnelData
    risk_heatmap: RiskHeatmapData
    top_deals: list[DealSummary]
    at_risk_deals: list[DealSummary]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_window: str = "current_quarter"
