from __future__ import annotations

from datetime import datetime

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from app.dependencies import get_db, get_redis
from app.schemas.common import APIResponse
from app.schemas.data_sources import DataProvenanceSummary, DataSourceHealth

router = APIRouter()


@router.get("")
async def liveness() -> dict[str, str]:
    """Basic liveness probe — confirms the process is running."""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness(
    request: Request,
    db: SQLModelAsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
) -> dict:
    """Readiness probe — verifies connectivity to Postgres and Redis."""
    checks: dict[str, str] = {}

    try:
        await db.exec(text("SELECT 1"))  # type: ignore[arg-type]
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}


@router.get("/data-sources", response_model=APIResponse[DataProvenanceSummary])
async def data_source_freshness() -> APIResponse[DataProvenanceSummary]:
    """Return freshness and health status for all configured data sources."""
    sources = [
        DataSourceHealth(
            name="OGD (data.gov.in)",
            status="healthy",
            data_freshness="Placeholder — implement actual check",
            tier=1,
        ),
        DataSourceHealth(
            name="MCA (Ministry of Corporate Affairs)",
            status="healthy",
            data_freshness="Placeholder — implement actual check",
            tier=1,
        ),
        DataSourceHealth(
            name="BSE India",
            status="healthy",
            data_freshness="Placeholder — implement actual check",
            tier=2,
        ),
        DataSourceHealth(
            name="NSE India",
            status="healthy",
            data_freshness="Placeholder — implement actual check",
            tier=2,
        ),
    ]

    healthy = [s for s in sources if s.status == "healthy"]
    degraded = [s for s in sources if s.status == "degraded"]
    down = [s for s in sources if s.status == "down"]

    summary = DataProvenanceSummary(
        sources=sources,
        overall_health="healthy" if len(down) == 0 and len(degraded) == 0 else "degraded",
        total_sources=len(sources),
        healthy_count=len(healthy),
        degraded_count=len(degraded),
        down_count=len(down),
        stale_count=0,
    )
    return APIResponse(data=summary)
