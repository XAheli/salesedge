"""Competitive intelligence endpoints — signals, trends, market data."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Query
from sqlmodel import select, col

from app.dependencies import DBSession
from app.models.signal import Signal
from app.models.deal import Deal
from app.models.prospect import Prospect
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/overview", response_model=APIResponse[dict])
async def intelligence_overview(db: DBSession) -> APIResponse[dict]:
    sig_result = await db.exec(select(Signal).order_by(col(Signal.created_at).desc()))
    signals = sig_result.all()

    type_groups: dict[str, list] = {}
    for s in signals:
        t = s.signal_type or "other"
        if t not in type_groups:
            type_groups[t] = []
        type_groups[t].append({
            "id": str(s.id),
            "title": s.title,
            "summary": s.summary,
            "source": s.source,
            "impact_score": s.impact_score,
            "published_at": s.published_at.isoformat() if s.published_at else None,
            "source_url": s.source_url,
        })

    deal_result = await db.exec(select(Deal).where(Deal.competitor_mentions > 0))
    competitive_deals = deal_result.all()
    competitor_deal_count = len(competitive_deals)

    p_result = await db.exec(select(Prospect))
    all_prospects = p_result.all()
    industry_counts = Counter(p.industry for p in all_prospects if p.industry)

    policy_signals = type_groups.get("policy_rate_change", []) + type_groups.get("regulatory_update", []) + type_groups.get("budget_announcement", [])
    competitor_signals = type_groups.get("competitor_funding", [])
    market_signals = type_groups.get("industry_news", []) + type_groups.get("economic_indicator", []) + type_groups.get("technology_change", [])

    overview = {
        "total_signals": len(signals),
        "signal_types": {k: len(v) for k, v in type_groups.items()},
        "policy_signals": policy_signals[:10],
        "competitor_signals": competitor_signals[:10],
        "market_signals": market_signals[:10],
        "deals_with_competitors": competitor_deal_count,
        "industry_coverage": dict(industry_counts.most_common(10)),
        "latest_signals": [
            {
                "id": str(s.id), "title": s.title, "type": s.signal_type,
                "impact": s.impact_score, "source": s.source,
                "published": s.published_at.isoformat() if s.published_at else None,
            }
            for s in signals[:15]
        ],
    }
    return APIResponse(data=overview)
