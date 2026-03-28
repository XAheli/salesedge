from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.dependencies import DBSession, RedisClient
from app.models.deal import Deal
from app.models.prospect import Prospect
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.deals import DealDetail, DealSummary

router = APIRouter()


@router.get("", response_model=PaginatedResponse[DealSummary])
async def list_deals(
    db: DBSession,
    stage: str | None = Query(None),
    owner: str | None = Query(None),
    min_value: float | None = Query(None),
    max_value: float | None = Query(None),
    sort_by: str = Query("value_inr"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
) -> PaginatedResponse[DealSummary]:
    """List deals with optional filters and pagination."""
    query = select(Deal, Prospect.company_name).join(
        Prospect, Deal.prospect_id == Prospect.id, isouter=True
    )

    if stage:
        query = query.where(Deal.stage == stage)
    if owner:
        query = query.where(Deal.owner == owner)
    if min_value is not None:
        query = query.where(Deal.value_inr >= min_value)
    if max_value is not None:
        query = query.where(Deal.value_inr <= max_value)

    sort_col = getattr(Deal, sort_by, Deal.value_inr)
    query = query.order_by(sort_col.desc() if sort_order == "desc" else sort_col.asc())

    offset = (page - 1) * page_size
    paginated = query.offset(offset).limit(page_size)
    result = await db.exec(paginated)  # type: ignore[arg-type]
    rows = result.all()

    items = [
        DealSummary(
            id=deal.id,
            prospect_name=company_name or "Unknown",
            stage=deal.stage,
            value_inr=deal.value_inr,
            risk_score=deal.risk_score or 0.0,
            days_in_stage=deal.days_in_stage,
            owner=deal.owner,
            last_activity=deal.updated_at,
        )
        for deal, company_name in rows
    ]

    return PaginatedResponse(items=items, total=len(items), page=page, page_size=page_size)


@router.get("/risk-summary", response_model=APIResponse[dict])
async def deal_risk_summary(db: DBSession) -> APIResponse[dict]:
    """Return an aggregated risk view across all active deals."""
    result = await db.exec(
        select(Deal).where(Deal.actual_outcome.is_(None))  # type: ignore[arg-type, union-attr]
    )
    active_deals = result.all()

    risk_buckets: dict[str, list[str]] = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
    }
    for deal in active_deals:
        score = deal.risk_score or 0.0
        if score >= 80:
            risk_buckets["critical"].append(str(deal.id))
        elif score >= 60:
            risk_buckets["high"].append(str(deal.id))
        elif score >= 30:
            risk_buckets["medium"].append(str(deal.id))
        else:
            risk_buckets["low"].append(str(deal.id))

    summary = {
        "total_active": len(active_deals),
        "risk_distribution": {k: len(v) for k, v in risk_buckets.items()},
        "critical_deal_ids": risk_buckets["critical"],
        "high_deal_ids": risk_buckets["high"],
    }
    return APIResponse(data=summary)


@router.get("/{deal_id}", response_model=APIResponse[DealDetail])
async def get_deal(deal_id: UUID, db: DBSession) -> APIResponse[DealDetail]:
    """Retrieve full deal detail by ID."""
    deal = await db.get(Deal, deal_id)
    if deal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deal not found")

    prospect = await db.get(Prospect, deal.prospect_id)
    prospect_name = prospect.company_name if prospect else "Unknown"

    detail = DealDetail(
        id=deal.id,
        prospect_name=prospect_name,
        stage=deal.stage,
        value_inr=deal.value_inr,
        risk_score=deal.risk_score or 0.0,
        days_in_stage=deal.days_in_stage,
        owner=deal.owner,
        last_activity=deal.updated_at,
        expected_close_date=deal.expected_close_date,
        win_probability=deal.win_probability,
        engagement_score=deal.engagement_score,
    )
    return APIResponse(data=detail)
