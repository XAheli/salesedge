"""Signal feed endpoints — returns real signals from DB."""
from __future__ import annotations

from fastapi import APIRouter, Query
from sqlmodel import select, col, func

from app.dependencies import DBSession
from app.models.signal import Signal
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("", response_model=APIResponse[dict])
async def list_signals(
    db: DBSession,
    signal_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> APIResponse[dict]:
    query = select(Signal).order_by(col(Signal.created_at).desc()).limit(limit)
    if signal_type:
        query = query.where(Signal.signal_type == signal_type)
    result = await db.exec(query)
    signals = result.all()
    items = [
        {
            "id": str(s.id),
            "source": s.source,
            "type": s.signal_type,
            "title": s.title,
            "summary": s.summary,
            "impact_score": s.impact_score,
            "source_url": s.source_url,
            "published_at": s.published_at.isoformat() if s.published_at else None,
            "created_at": s.created_at.isoformat(),
        }
        for s in signals
    ]
    types_result = await db.exec(select(Signal.signal_type, func.count()).group_by(Signal.signal_type))
    type_counts = {row[0]: row[1] for row in types_result.all()}
    return APIResponse(data={"signals": items, "total": len(items), "type_counts": type_counts})
