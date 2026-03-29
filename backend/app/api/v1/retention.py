"""Retention and churn endpoints — computed from real deal data."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Query
from sqlmodel import select

from app.config import classify_risk
from app.dependencies import DBSession
from app.models.deal import Deal
from app.models.prospect import Prospect
from app.schemas.common import APIResponse
from app.services.scoring.churn_predictor import ChurnPredictor, CustomerData

router = APIRouter()

_churn_predictor = ChurnPredictor()


def _build_customer_data(deal: Deal, company_name: str) -> CustomerData:
    """Map available Deal fields to the ChurnPredictor feature vector."""
    now = datetime.utcnow()
    renewal_proximity = 0.0
    if deal.expected_close_date:
        renewal_proximity = max(0, (deal.expected_close_date - now).days) / 365
    return CustomerData(
        customer_id=str(deal.id),
        company_name=company_name,
        usage_trend_30d=((deal.engagement_score or 50) - 50) / 50,
        competitive_mentions=float(deal.competitor_mentions),
        contract_renewal_proximity=renewal_proximity,
        macro_headwind=(deal.risk_score or 0) / 100,
    )


@router.get("/overview", response_model=APIResponse[dict])
async def retention_overview(db: DBSession) -> APIResponse[dict]:
    result = await db.exec(select(Deal))
    all_deals = result.all()

    won = [d for d in all_deals if d.stage == "Won"]
    lost = [d for d in all_deals if d.stage == "Lost"]
    active = [d for d in all_deals if d.actual_outcome is None and d.stage not in ("Won", "Lost")]

    at_risk = [d for d in active if (d.risk_score or 0) > 50]

    stage_retention: dict[str, dict] = {}
    for d in all_deals:
        if d.stage not in stage_retention:
            stage_retention[d.stage] = {"total": 0, "won": 0, "lost": 0, "active": 0}
        stage_retention[d.stage]["total"] += 1
        if d.stage == "Won":
            stage_retention[d.stage]["won"] += 1
        elif d.stage == "Lost":
            stage_retention[d.stage]["lost"] += 1
        else:
            stage_retention[d.stage]["active"] += 1

    risk_buckets = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for d in active:
        score = d.risk_score or 0
        risk_buckets[classify_risk(score)] += 1

    at_risk_details = []
    for d in sorted(at_risk, key=lambda x: -(x.risk_score or 0))[:10]:
        p = await db.get(Prospect, d.prospect_id)
        company_name = p.company_name if p else "Unknown"
        prediction = _churn_predictor.predict(_build_customer_data(d, company_name))
        at_risk_details.append({
            "id": str(d.id),
            "company": company_name,
            "value_inr": d.value_inr,
            "risk_score": d.risk_score,
            "stage": d.stage,
            "days_in_stage": d.days_in_stage,
            "owner": d.owner,
            "churn_probability": prediction.probability,
            "contributing_factors": prediction.contributing_factors,
        })

    loss_reasons = Counter(d.loss_reason or "Unknown" for d in lost)

    overview = {
        "total_customers": len(won),
        "at_risk_count": len(at_risk),
        "lost_count": len(lost),
        "active_pipeline": len(active),
        "retention_rate": round(len(won) / max(1, len(won) + len(lost)) * 100, 1),
        "avg_risk_score": round(sum(d.risk_score or 0 for d in active) / max(1, len(active)), 2),
        "risk_distribution": risk_buckets,
        "at_risk_deals": at_risk_details,
        "loss_reasons": dict(loss_reasons.most_common(5)),
        "total_value_at_risk": sum(d.value_inr for d in at_risk),
        "stage_breakdown": stage_retention,
    }
    return APIResponse(data=overview)


@router.get("/cohorts", response_model=APIResponse[dict])
async def retention_cohorts(db: DBSession) -> APIResponse[dict]:
    """Return cohort retention data grouped by quarter of deal creation."""
    result = await db.exec(select(Deal))
    all_deals = result.all()

    cohorts: dict[str, dict] = {}
    for d in all_deals:
        q = f"{d.created_at.year}-Q{(d.created_at.month - 1) // 3 + 1}" if d.created_at else "Unknown"
        if q not in cohorts:
            cohorts[q] = {"total": 0, "won": 0, "lost": 0, "active": 0, "total_value": 0.0}
        cohorts[q]["total"] += 1
        cohorts[q]["total_value"] += d.value_inr
        if d.stage == "Won":
            cohorts[q]["won"] += 1
        elif d.stage == "Lost":
            cohorts[q]["lost"] += 1
        else:
            cohorts[q]["active"] += 1

    for key, c in cohorts.items():
        closed = c["won"] + c["lost"]
        c["retention_rate"] = round(c["won"] / max(1, closed) * 100, 1)

    return APIResponse(data={
        "cohorts": cohorts,
        "total_cohorts": len(cohorts),
    })


@router.get("/churn-predictions", response_model=APIResponse[dict])
async def churn_predictions(
    db: DBSession,
    threshold: float = Query(50, ge=0, le=100, description="Minimum risk score (0-100) to flag"),
) -> APIResponse[dict]:
    """Return churn predictions for all at-risk deals above the threshold."""
    result = await db.exec(select(Deal).where(Deal.actual_outcome.is_(None)))  # type: ignore[union-attr]
    active_deals = result.all()

    predictions = []
    for d in sorted(active_deals, key=lambda x: -(x.risk_score or 0)):
        if (d.risk_score or 0) < threshold:
            continue
        p = await db.get(Prospect, d.prospect_id)
        company_name = p.company_name if p else "Unknown"
        prediction = _churn_predictor.predict(_build_customer_data(d, company_name))
        predictions.append({
            "deal_id": str(d.id),
            "company": company_name,
            "value_inr": d.value_inr,
            "stage": d.stage,
            "risk_score": d.risk_score,
            "churn_probability": prediction.probability,
            "risk_level": prediction.risk_level,
            "contributing_factors": prediction.contributing_factors,
            "days_in_stage": d.days_in_stage,
            "owner": d.owner,
            "recommended_action": (
                "Immediate executive escalation" if prediction.risk_level == "critical"
                else "Schedule retention call" if prediction.risk_level == "high"
                else "Monitor closely"
            ),
        })

    return APIResponse(data={
        "predictions": predictions,
        "total_at_risk": len(predictions),
        "total_value_at_risk": sum(p["value_inr"] for p in predictions),
        "threshold": threshold,
    })


@router.get("/customers/{customer_id}/health", response_model=APIResponse[dict])
async def customer_health(db: DBSession, customer_id: str) -> APIResponse[dict]:
    """Return health metrics for a specific customer (prospect) across their deals."""
    from uuid import UUID
    from fastapi import HTTPException, status as http_status

    try:
        pid = UUID(customer_id)
    except ValueError:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail="Invalid customer ID format")

    prospect = await db.get(Prospect, pid)
    if not prospect:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Customer not found")

    deal_result = await db.exec(select(Deal).where(Deal.prospect_id == pid))
    deals = deal_result.all()

    won = [d for d in deals if d.stage == "Won"]
    lost = [d for d in deals if d.stage == "Lost"]
    active = [d for d in deals if d.actual_outcome is None and d.stage not in ("Won", "Lost")]

    avg_risk = round(sum(d.risk_score or 0 for d in active) / max(1, len(active)), 2) if active else 0
    avg_engagement = round(sum(d.engagement_score or 0 for d in active) / max(1, len(active)), 2) if active else 0

    if avg_risk >= 70:
        health_status = "critical"
    elif avg_risk >= 50:
        health_status = "at_risk"
    elif avg_risk >= 30:
        health_status = "needs_attention"
    else:
        health_status = "healthy"

    return APIResponse(data={
        "customer_id": customer_id,
        "company_name": prospect.company_name,
        "health_status": health_status,
        "avg_risk_score": avg_risk,
        "avg_engagement_score": avg_engagement,
        "total_deals": len(deals),
        "won_deals": len(won),
        "lost_deals": len(lost),
        "active_deals": len(active),
        "total_value": sum(d.value_inr for d in deals),
        "active_value": sum(d.value_inr for d in active),
        "deal_summary": [
            {
                "id": str(d.id),
                "title": d.title,
                "stage": d.stage,
                "value_inr": d.value_inr,
                "risk_score": d.risk_score,
                "days_in_stage": d.days_in_stage,
            }
            for d in deals
        ],
    })
