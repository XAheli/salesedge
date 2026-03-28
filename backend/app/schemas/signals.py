from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Signal(BaseModel):
    """An individual signal detected by the ingestion pipeline."""

    id: UUID
    source: str = Field(description="e.g. 'ogd', 'mca', 'bse', 'news', 'linkedin'")
    signal_type: str = Field(
        description="e.g. 'funding', 'leadership_change', 'expansion', 'policy_update'"
    )
    title: str
    summary: str
    impact_score: float = Field(ge=0.0, le=10.0)
    affected_deals: list[UUID] = Field(default_factory=list)
    affected_prospects: list[UUID] = Field(default_factory=list)
    timestamp: datetime
    source_url: str | None = None
    is_read: bool = False
    is_actionable: bool = True


class SignalFeed(BaseModel):
    """Paginated signal feed response."""

    signals: list[Signal]
    total: int
    unread_count: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
