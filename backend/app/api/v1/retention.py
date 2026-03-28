"""Retention and churn endpoints — computed from real deal data."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Query
from sqlmodel import select

from app.dependencies import DBSession
from app.models.deal import Deal
from app.models.prospect import Prospect
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/overview", response_model=APIResponse[dict])
async def retention_overview(db: DBSession) -> APIResponse[dict]:
    result = await db.exec(select(Deal))
    all_deals = result.all()

    won = [d for d in all_deals if d.stage == "Won"]
    lost = [d for d in all_deals if d.stage == "Lost"]
    active = [d for d in all_deals if d.actual_outcome is None and d.stage not in ("Won", "Lost")]

    at_risk = [d for d in active if (d.risk_score or 0) > 0.5]

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
        if score >= 0.7: risk_buckets["critical"] += 1
        elif score >= 0.5: risk_buckets["high"] += 1
        elif score >= 0.3: risk_buckets["medium"] += 1
        else: risk_buckets["low"] += 1

    at_risk_details = []
    for d in sorted(at_risk, key=lambda x: -(x.risk_score or 0))[:10]:
        p = await db.get(Prospect, d.prospect_id)
        at_risk_details.append({
            "id": str(d.id),
            "company": p.company_name if p else "Unknown",
            "value_inr": d.value_inr,
            "risk_score": d.risk_score,
            "stage": d.stage,
            "days_in_stage": d.days_in_stage,
            "owner": d.owner,
            "churn_probability": min(0.95, (d.risk_score or 0) * 1.2),
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
