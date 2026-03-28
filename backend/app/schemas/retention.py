from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CustomerHealthSummary(BaseModel):
    """Health score and key signals for an existing customer."""

    customer_id: UUID
    company_name: str
    health_score: float = Field(ge=0.0, le=100.0)
    health_trend: str = Field(description="improving, stable, or declining")
    nps_score: int | None = Field(None, ge=-100, le=100)
    usage_trend_pct: float | None = None
    support_ticket_velocity: float | None = None
    last_engagement: datetime | None = None
    contract_end_date: datetime | None = None
    arr_inr: float | None = None


class ChurnPrediction(BaseModel):
    """ML-generated churn probability and contributing factors."""

    customer_id: UUID
    company_name: str
    churn_probability: float = Field(ge=0.0, le=1.0)
    prediction_confidence: float = Field(ge=0.0, le=1.0)
    risk_tier: str = Field(description="critical, high, medium, low")
    top_risk_factors: list[str]
    recommended_actions: list[str]
    predicted_churn_window: str | None = Field(
        None, description="e.g. 'next 30 days', 'next 90 days'"
    )
    model_version: str | None = None
    predicted_at: datetime


class RetentionCohort(BaseModel):
    """Cohort-level retention analysis."""

    cohort_label: str = Field(description="e.g. 'Q1 FY25', 'Jan 2025'")
    start_count: int
    retained_count: int
    retention_rate: float = Field(ge=0.0, le=100.0)
    avg_health_score: float
    avg_arr_inr: float
    churned_arr_inr: float
    expanded_arr_inr: float
    net_retention_pct: float


class InterventionRecord(BaseModel):
    """Record of a retention intervention taken for a customer."""

    id: UUID
    customer_id: UUID
    intervention_type: str = Field(
        description="executive_outreach, qbr, discount, feature_unlock, training, escalation"
    )
    triggered_by: str = Field(description="automated or manual")
    status: str = Field(description="planned, in_progress, completed, skipped")
    assigned_to: str | None = None
    notes: str | None = None
    outcome: str | None = None
    impact_on_health: float | None = Field(
        None, description="Change in health score after intervention"
    )
    created_at: datetime
    completed_at: datetime | None = None
