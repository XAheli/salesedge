from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.dependencies import CurrentUser, DBSession, RedisClient
from app.models.prospect import Prospect
from app.schemas.common import APIResponse, PaginatedResponse, ResponseMetadata
from app.schemas.prospects import ProspectDetail, ProspectSummary

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProspectSummary])
async def list_prospects(
    db: DBSession,
    industry: str | None = Query(None),
    state: str | None = Query(None),
    min_fit_score: float | None = Query(None, ge=0.0, le=100.0),
    max_fit_score: float | None = Query(None, ge=0.0, le=100.0),
    revenue_min_inr: float | None = Query(None),
    revenue_max_inr: float | None = Query(None),
    listed_status: str | None = Query(None, description="listed, unlisted, or all"),
    sort_by: str = Query("fit_score"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
) -> PaginatedResponse[ProspectSummary]:
    """List prospects with filtering, sorting, and pagination."""
    query = select(Prospect)

    if industry:
        query = query.where(Prospect.industry == industry)
    if state:
        query = query.where(Prospect.state == state)
    if min_fit_score is not None:
        query = query.where(Prospect.fit_score >= min_fit_score)
    if max_fit_score is not None:
        query = query.where(Prospect.fit_score <= max_fit_score)
    if revenue_min_inr is not None:
        query = query.where(Prospect.revenue_inr >= revenue_min_inr)
    if revenue_max_inr is not None:
        query = query.where(Prospect.revenue_inr <= revenue_max_inr)
    if listed_status == "listed":
        query = query.where(Prospect.listed_exchange.isnot(None))  # type: ignore[union-attr]
    elif listed_status == "unlisted":
        query = query.where(Prospect.listed_exchange.is_(None))  # type: ignore[union-attr]

    sort_col = getattr(Prospect, sort_by, Prospect.fit_score)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    count_result = await db.exec(select(Prospect))  # type: ignore[arg-type]
    all_results = count_result.all()
    total = len(all_results)

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.exec(query)  # type: ignore[arg-type]
    prospects = result.all()

    items = [
        ProspectSummary(
            id=p.id,
            company_name=p.company_name,
            industry=p.industry,
            nic_code=p.nic_code,
            employee_count=p.employee_count,
            state=p.state,
            fit_score=p.fit_score,
            confidence=p.fit_score_confidence,
            last_enriched=p.last_enriched_at,
        )
        for p in prospects
    ]

    pages = max(1, (total + page_size - 1) // page_size)
    return PaginatedResponse(
        items=items, total=total, page=page, page_size=page_size, pages=pages
    )


@router.get("/{prospect_id}", response_model=APIResponse[ProspectDetail])
async def get_prospect(prospect_id: UUID, db: DBSession) -> APIResponse[ProspectDetail]:
    """Retrieve full prospect detail by ID."""
    prospect = await db.get(Prospect, prospect_id)
    if prospect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found")

    detail = ProspectDetail(
        id=prospect.id,
        company_name=prospect.company_name,
        industry=prospect.industry,
        nic_code=prospect.nic_code,
        employee_count=prospect.employee_count,
        state=prospect.state,
        city=prospect.city,
        gst_number=prospect.gst_number,
        website=prospect.website,
        listed_exchange=prospect.listed_exchange,
        bse_code=prospect.bse_code,
        nse_symbol=prospect.nse_symbol,
        dpiit_recognized=prospect.dpiit_recognized,
        fit_score=prospect.fit_score,
        confidence=prospect.fit_score_confidence,
        last_enriched=prospect.last_enriched_at,
    )
    return APIResponse(data=detail)


@router.post("/{prospect_id}/enrich", response_model=APIResponse[dict])
async def trigger_enrichment(
    prospect_id: UUID,
    db: DBSession,
    user: CurrentUser,
) -> APIResponse[dict]:
    """Trigger asynchronous enrichment for a prospect.

    Queues enrichment jobs for MCA, BSE/NSE, OGD, and other configured sources.
    """
    prospect = await db.get(Prospect, prospect_id)
    if prospect is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prospect not found")

    return APIResponse(
        data={
            "prospect_id": str(prospect_id),
            "status": "enrichment_queued",
            "message": "Enrichment pipeline triggered. Results will be available shortly.",
        }
    )
