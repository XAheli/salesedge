"""Data provenance endpoints — real health-check probes for each connector."""
from __future__ import annotations

import time
from datetime import datetime

import httpx
import structlog
from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.schemas.common import APIResponse
from app.schemas.data_sources import DataProvenanceSummary, DataSourceHealth

logger = structlog.get_logger(__name__)
router = APIRouter()

_HEALTH_TIMEOUT = 5.0
_DEGRADED_THRESHOLD_MS = 3000.0

_BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}


def _relative_freshness(dt: datetime) -> str:
    """Compute a human-readable relative time string from a datetime to now."""
    delta = datetime.utcnow() - dt
    total_seconds = int(delta.total_seconds())

    if total_seconds < 60:
        return f"{total_seconds} seconds ago"
    minutes = total_seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        remaining_min = minutes % 60
        if remaining_min:
            return f"{hours} hour{'s' if hours != 1 else ''} {remaining_min} min ago"
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


async def _probe(
    name: str,
    url: str,
    tier: int,
    *,
    headers: dict[str, str] | None = None,
    requires_key: bool = False,
    key_configured: bool = True,
) -> DataSourceHealth:
    """Make a real HTTP health-check call and return measured health."""
    if requires_key and not key_configured:
        return DataSourceHealth(name=name, status="not_configured", tier=tier)

    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=_HEALTH_TIMEOUT) as client:
            resp = await client.get(url, headers=headers or {})
            elapsed_ms = (time.monotonic() - start) * 1000
            now = datetime.utcnow()
            if resp.status_code < 300:
                health = "degraded" if elapsed_ms > _DEGRADED_THRESHOLD_MS else "healthy"
            else:
                health = "degraded"
            return DataSourceHealth(
                name=name,
                status=health,
                last_check=now,
                response_time_ms=round(elapsed_ms, 1),
                error_rate=0.0,
                data_freshness=_relative_freshness(now),
                tier=tier,
            )
    except Exception as exc:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.warning("health_check_failed", source=name, error=str(exc))
        return DataSourceHealth(
            name=name,
            status="down",
            last_check=datetime.utcnow(),
            response_time_ms=round(elapsed_ms, 1),
            error_rate=1.0,
            data_freshness="unknown",
            tier=tier,
        )


async def _build_sources() -> list[DataSourceHealth]:
    """Build source list by performing real health-check probes."""
    settings = get_settings()
    sources: list[DataSourceHealth] = []

    ogd_key = settings.ogd_api_key
    sources.append(await _probe(
        "OGD (data.gov.in)",
        f"https://api.data.gov.in/lists?format=json&api-key={ogd_key}&limit=1",
        tier=1,
        requires_key=True,
        key_configured=bool(ogd_key),
    ))

    sources.append(DataSourceHealth(
        name="MCA (Ministry of Corporate Affairs)", status="not_configured", tier=1,
    ))

    sources.append(await _probe(
        "BSE India",
        "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w?scripcode=500325",
        tier=2,
    ))

    sources.append(await _probe(
        "NSE India",
        "https://www.nseindia.com/api/marketStatus",
        tier=2,
        headers=_BROWSER_HEADERS,
    ))

    finnhub_key = settings.finnhub_api_key
    if finnhub_key:
        sources.append(await _probe(
            "Finnhub",
            f"https://finnhub.io/api/v1/stock/market-status?exchange=US&token={finnhub_key}",
            tier=3,
        ))
    else:
        sources.append(DataSourceHealth(name="Finnhub", status="not_configured", tier=3))

    return sources


@router.get("", response_model=APIResponse[DataProvenanceSummary])
async def list_data_sources() -> APIResponse[DataProvenanceSummary]:
    """Return health and freshness for all configured data sources."""
    sources = await _build_sources()

    healthy = [s for s in sources if s.status == "healthy"]
    degraded = [s for s in sources if s.status == "degraded"]
    down = [s for s in sources if s.status == "down"]

    overall = "healthy"
    if down:
        overall = "critical"
    elif degraded:
        overall = "degraded"

    summary = DataProvenanceSummary(
        sources=sources,
        overall_health=overall,
        total_sources=len(sources),
        healthy_count=len(healthy),
        degraded_count=len(degraded),
        down_count=len(down),
    )
    return APIResponse(data=summary)


@router.get("/{source_id}/health", response_model=APIResponse[DataSourceHealth])
async def get_source_health(source_id: str) -> APIResponse[DataSourceHealth]:
    """Return health details for a single data source by name slug."""
    sources = await _build_sources()
    index = {s.name.lower(): s for s in sources}
    source = index.get(source_id.lower().replace("-", " "))
    if source is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_id}' not found",
        )
    return APIResponse(data=source)
