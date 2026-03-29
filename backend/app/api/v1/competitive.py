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


@router.get("/mentions", response_model=APIResponse[dict])
async def competitor_mentions(
    db: DBSession,
    limit: int = Query(50, ge=1, le=200),
) -> APIResponse[dict]:
    """Return deals with competitor mentions and related signals."""
    deal_result = await db.exec(
        select(Deal, Prospect.company_name)
        .join(Prospect, Deal.prospect_id == Prospect.id, isouter=True)
        .where(Deal.competitor_mentions > 0)
        .order_by(col(Deal.competitor_mentions).desc())
        .limit(limit)
    )
    rows = deal_result.all()

    mentions = [
        {
            "deal_id": str(d.id),
            "company": name or "Unknown",
            "title": d.title,
            "stage": d.stage,
            "competitor_mentions": d.competitor_mentions,
            "value_inr": d.value_inr,
            "risk_score": d.risk_score,
            "owner": d.owner,
        }
        for d, name in rows
    ]

    return APIResponse(data={
        "mentions": mentions,
        "total": len(mentions),
    })


@router.get("/battlecards", response_model=APIResponse[dict])
async def battlecards(db: DBSession) -> APIResponse[dict]:
    """Return generated battlecards derived from competitor signals."""
    sig_result = await db.exec(
        select(Signal)
        .where(col(Signal.signal_type) == "competitor_funding")
        .order_by(col(Signal.created_at).desc())
    )
    competitor_signals = sig_result.all()

    cards = []
    for s in competitor_signals:
        cards.append({
            "id": str(s.id),
            "competitor": s.title,
            "summary": s.summary,
            "impact_score": s.impact_score,
            "source": s.source,
            "source_url": s.source_url,
            "published_at": s.published_at.isoformat() if s.published_at else None,
            "counter_strategy": (
                "High-impact — prepare executive briefing"
                if s.impact_score >= 7.0
                else "Monitor and update positioning"
            ),
        })

    return APIResponse(data={
        "battlecards": cards,
        "total": len(cards),
    })


@router.get("/policy-signals", response_model=APIResponse[dict])
async def policy_signals(
    db: DBSession,
    limit: int = Query(30, ge=1, le=100),
) -> APIResponse[dict]:
    """Return policy-related signals (regulatory, budget, rate changes)."""
    policy_types = ("policy_rate_change", "regulatory_update", "budget_announcement")
    sig_result = await db.exec(
        select(Signal)
        .where(col(Signal.signal_type).in_(policy_types))
        .order_by(col(Signal.created_at).desc())
        .limit(limit)
    )
    signals = sig_result.all()

    items = [
        {
            "id": str(s.id),
            "title": s.title,
            "summary": s.summary,
            "signal_type": s.signal_type,
            "impact_score": s.impact_score,
            "source": s.source,
            "source_url": s.source_url,
            "published_at": s.published_at.isoformat() if s.published_at else None,
        }
        for s in signals
    ]

    return APIResponse(data={
        "signals": items,
        "total": len(items),
    })


@router.get("/market-signals", response_model=APIResponse[dict])
async def market_signals(
    db: DBSession,
    limit: int = Query(30, ge=1, le=100),
) -> APIResponse[dict]:
    """Return market-related signals (industry news, economic indicators, tech changes)."""
    market_types = ("industry_news", "economic_indicator", "technology_change")
    sig_result = await db.exec(
        select(Signal)
        .where(col(Signal.signal_type).in_(market_types))
        .order_by(col(Signal.created_at).desc())
        .limit(limit)
    )
    signals = sig_result.all()

    items = [
        {
            "id": str(s.id),
            "title": s.title,
            "summary": s.summary,
            "signal_type": s.signal_type,
            "impact_score": s.impact_score,
            "source": s.source,
            "source_url": s.source_url,
            "published_at": s.published_at.isoformat() if s.published_at else None,
        }
        for s in signals
    ]

    return APIResponse(data={
        "signals": items,
        "total": len(items),
    })
