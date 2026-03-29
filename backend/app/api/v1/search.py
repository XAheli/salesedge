"""Global search across all entities."""
from __future__ import annotations

from fastapi import APIRouter, Query
from sqlmodel import select, col, or_

from app.dependencies import DBSession
from app.models.prospect import Prospect
from app.models.deal import Deal
from app.models.signal import Signal
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get("", response_model=PaginatedResponse[dict])
async def global_search(
    db: DBSession,
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
) -> PaginatedResponse[dict]:
    pattern = f"%{q}%"

    p_result = await db.exec(
        select(Prospect)
        .where(or_(
            col(Prospect.company_name).ilike(pattern),
            col(Prospect.industry).ilike(pattern),
            col(Prospect.state).ilike(pattern),
            col(Prospect.nse_symbol).ilike(pattern),
        ))
        .limit(limit)
    )
    prospects = [
        {"id": str(p.id), "type": "prospect", "title": p.company_name, "subtitle": f"{p.industry} · {p.state}"}
        for p in p_result.all()
    ]

    d_result = await db.exec(
        select(Deal, Prospect.company_name)
        .join(Prospect, Deal.prospect_id == Prospect.id, isouter=True)
        .where(or_(
            col(Deal.title).ilike(pattern),
            col(Deal.owner).ilike(pattern),
            col(Prospect.company_name).ilike(pattern),
        ))
        .limit(limit)
    )
    deals = [
        {"id": str(d.id), "type": "deal", "title": d.title or name, "subtitle": f"{d.stage} · {d.owner}"}
        for d, name in d_result.all()
    ]

    s_result = await db.exec(
        select(Signal)
        .where(or_(
            col(Signal.title).ilike(pattern),
            col(Signal.summary).ilike(pattern),
            col(Signal.source).ilike(pattern),
        ))
        .limit(limit)
    )
    signals = [
        {"id": str(s.id), "type": "signal", "title": s.title, "subtitle": f"{s.source} · {s.signal_type}"}
        for s in s_result.all()
    ]

    results = prospects + deals + signals
    return PaginatedResponse(items=results, total=len(results), page=1, page_size=limit)
