from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class SourceAttribution(BaseModel):
    """Provenance metadata for a data point."""

    source_name: str
    source_url: str | None = None
    last_updated: datetime | None = None
    reliability_tier: int = Field(ge=1, le=3, description="1=Gov/Official, 2=Market, 3=Enrichment")


class ResponseMetadata(BaseModel):
    """Standard metadata attached to every API response."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str | None = None
    data_freshness: str | None = Field(
        None, description="Human-readable freshness, e.g. '2 hours ago'"
    )
    source_attribution: list[SourceAttribution] = Field(default_factory=list)
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    cache_status: str | None = Field(None, description="HIT, MISS, or STALE")


class ErrorDetail(BaseModel):
    """Structured error information."""

    code: str
    message: str
    details: dict | None = None


class APIResponse(BaseModel, Generic[T]):
    """Standardised envelope for all API responses."""

    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None
    meta: ResponseMetadata = Field(default_factory=ResponseMetadata)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response with total counts."""

    items: list[T]
    total: int
    page: int = 1
    page_size: int = 25
    pages: int = 1
    meta: ResponseMetadata = Field(default_factory=ResponseMetadata)
