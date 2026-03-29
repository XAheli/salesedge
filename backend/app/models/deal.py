from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.base import AuditMixin


class Deal(AuditMixin, table=True):
    """A sales deal linked to a prospect, with risk scoring and outcome tracking."""

    __tablename__ = "deals"

    prospect_id: UUID = Field(foreign_key="prospects.id", index=True)
    title: str = Field(max_length=512)
    stage: str = Field(max_length=100, index=True)
    value_inr: float = Field(ge=0, description="Deal value in INR")
    expected_close_date: datetime | None = Field(default=None)
    owner: str | None = Field(default=None, max_length=255, index=True)
    risk_score: float | None = Field(default=None, ge=0.0, le=100.0)
    risk_score_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    days_in_stage: int = Field(default=0)
    engagement_score: float | None = Field(default=None, ge=0.0, le=100.0)
    competitor_mentions: int = Field(default=0)
    win_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    actual_outcome: str | None = Field(
        default=None, max_length=20, description="won, lost, or abandoned"
    )
    closed_at: datetime | None = Field(default=None)
    loss_reason: str | None = Field(default=None, max_length=512)
