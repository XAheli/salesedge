from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DataSourceHealth(BaseModel):
    """Health and performance metrics for a single data source."""

    name: str
    status: str = Field(description="healthy, degraded, or down")
    last_check: datetime | None = None
    response_time_ms: float | None = None
    error_rate: float = Field(0.0, ge=0.0, le=1.0)
    data_freshness: str | None = Field(None, description="e.g. '45 minutes ago'")
    cache_hit_rate: float | None = Field(None, ge=0.0, le=1.0)
    records_ingested: int | None = None
    tier: int = Field(ge=1, le=3, description="1=Gov/Official, 2=Market, 3=Enrichment")


class DataProvenanceSummary(BaseModel):
    """Aggregate health overview across all data sources."""

    sources: list[DataSourceHealth]
    overall_health: str = Field(description="healthy, degraded, or critical")
    total_sources: int = 0
    healthy_count: int = 0
    degraded_count: int = 0
    down_count: int = 0
    stale_count: int = 0
    last_checked: datetime = Field(default_factory=datetime.utcnow)
