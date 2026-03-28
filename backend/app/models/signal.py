from __future__ import annotations

from datetime import datetime

from sqlmodel import Column, Field, SQLModel
from sqlalchemy import JSON

from app.models.base import AuditMixin


class Signal(AuditMixin, table=True):
    """An ingested signal from external data sources."""

    __tablename__ = "signals"

    source: str = Field(max_length=100, index=True)
    signal_type: str = Field(max_length=100, index=True)
    title: str = Field(max_length=512)
    summary: str
    impact_score: float = Field(ge=0.0, le=10.0)
    raw_data: dict | None = Field(default=None, sa_column=Column(JSON))
    source_url: str | None = Field(default=None, max_length=2048)
    published_at: datetime | None = Field(default=None)
    processed_at: datetime | None = Field(default=None)
    affected_entity_ids: list[str] | None = Field(default=None, sa_column=Column(JSON))
