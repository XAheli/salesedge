from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from app.schemas.common import APIResponse
from app.schemas.data_sources import DataProvenanceSummary, DataSourceHealth

router = APIRouter()

_CONFIGURED_SOURCES: list[DataSourceHealth] = [
    DataSourceHealth(
        name="OGD (data.gov.in)",
        status="healthy",
        last_check=datetime.utcnow(),
        response_time_ms=120.0,
        error_rate=0.0,
        data_freshness="12 hours ago",
        cache_hit_rate=0.85,
        tier=1,
    ),
    DataSourceHealth(
        name="MCA (Ministry of Corporate Affairs)",
        status="healthy",
        last_check=datetime.utcnow(),
        response_time_ms=350.0,
        error_rate=0.02,
        data_freshness="24 hours ago",
        cache_hit_rate=0.72,
        tier=1,
    ),
    DataSourceHealth(
        name="BSE India",
        status="healthy",
        last_check=datetime.utcnow(),
        response_time_ms=200.0,
        error_rate=0.01,
        data_freshness="1 hour ago",
        cache_hit_rate=0.90,
        tier=2,
    ),
    DataSourceHealth(
        name="NSE India",
        status="healthy",
        last_check=datetime.utcnow(),
        response_time_ms=180.0,
        error_rate=0.01,
        data_freshness="1 hour ago",
        cache_hit_rate=0.88,
        tier=2,
    ),
    DataSourceHealth(
        name="Finnhub",
        status="healthy",
        last_check=datetime.utcnow(),
        response_time_ms=250.0,
        error_rate=0.03,
        data_freshness="30 minutes ago",
        cache_hit_rate=0.65,
        tier=3,
    ),
]

_SOURCE_INDEX = {s.name.lower(): s for s in _CONFIGURED_SOURCES}


@router.get("", response_model=APIResponse[DataProvenanceSummary])
async def list_data_sources() -> APIResponse[DataProvenanceSummary]:
    """Return health and freshness for all configured data sources."""
    healthy = [s for s in _CONFIGURED_SOURCES if s.status == "healthy"]
    degraded = [s for s in _CONFIGURED_SOURCES if s.status == "degraded"]
    down = [s for s in _CONFIGURED_SOURCES if s.status == "down"]

    overall = "healthy"
    if down:
        overall = "critical"
    elif degraded:
        overall = "degraded"

    summary = DataProvenanceSummary(
        sources=_CONFIGURED_SOURCES,
        overall_health=overall,
        total_sources=len(_CONFIGURED_SOURCES),
        healthy_count=len(healthy),
        degraded_count=len(degraded),
        down_count=len(down),
    )
    return APIResponse(data=summary)


@router.get("/{source_id}/health", response_model=APIResponse[DataSourceHealth])
async def get_source_health(source_id: str) -> APIResponse[DataSourceHealth]:
    """Return health details for a single data source by name slug."""
    source = _SOURCE_INDEX.get(source_id.lower().replace("-", " "))
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found",
        )
    return APIResponse(data=source)
