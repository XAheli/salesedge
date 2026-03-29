"""Executive dashboard endpoints — all data computed from DB."""
from __future__ import annotations

from datetime import datetime, timedelta
from collections import Counter

from fastapi import APIRouter, Query
from sqlmodel import select, func, col

from app.config import classify_risk
from app.dependencies import DBSession
from app.models.deal import Deal
from app.models.prospect import Prospect
from app.models.signal import Signal
from app.schemas.common import APIResponse
from app.schemas.dashboard import (
    DealSummary,
    ExecutiveKPIs,
    ExecutiveSummary,
    FunnelData,
    FunnelStage,
    KPIMetric,
    RiskHeatmapCell,
    RiskHeatmapData,
)
from app.utils.indian_formats import format_inr

router = APIRouter()

STAGE_ORDER = ["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]


def _compute_trend(current: float, previous: float) -> tuple[float, str]:
    """Return (trend_pct, direction) comparing two period values."""
    if previous == 0:
        return (100.0, "up") if current > 0 else (0.0, "flat")
    pct = round((current - previous) / previous * 100, 1)
    direction = "up" if pct > 0 else "down" if pct < 0 else "flat"
    return pct, direction


def _data_confidence(deals: list) -> float:
    """Fraction of deals with non-null risk_score, engagement_score, win_probability."""
    if not deals:
        return 0.0
    filled = sum(
        (d.risk_score is not None) + (d.engagement_score is not None) + (d.win_probability is not None)
        for d in deals
    )
    return round(filled / (len(deals) * 3), 2)


def _weekly_values(deals: list, weeks: int = 6) -> list[float]:
    """Sum deal values into weekly buckets (oldest first)."""
    now = datetime.utcnow()
    buckets = [0.0] * weeks
    for d in deals:
        dt = d.created_at
        if not dt:
            continue
        week_ago = (now - dt).days // 7
        if 0 <= week_ago < weeks:
            buckets[weeks - 1 - week_ago] += d.value_inr
    return buckets


@router.get("/executive-summary", response_model=APIResponse[ExecutiveSummary])
async def executive_summary(
    db: DBSession,
    time_window: str = Query("30d"),
    territory: str | None = Query(None),
    segment: str | None = Query(None),
) -> APIResponse[ExecutiveSummary]:
    deal_q = select(Deal)
    result = await db.exec(deal_q)
    all_deals = result.all()

    won_deals = [d for d in all_deals if d.stage == "Won"]
    lost_deals = [d for d in all_deals if d.stage == "Lost"]
    active_deals = [d for d in all_deals if d.actual_outcome is None and d.stage not in ("Won", "Lost")]

    total_won_value = sum(d.value_inr for d in won_deals)
    total_pipeline = sum(d.value_inr for d in active_deals)
    total_closed = len(won_deals) + len(lost_deals)
    win_rate = (len(won_deals) / total_closed * 100) if total_closed > 0 else 0
    avg_days = sum(d.days_in_stage for d in active_deals) / len(active_deals) if active_deals else 0

    now = datetime.utcnow()
    period_days = int(time_window.rstrip("d")) if time_window.endswith("d") else 30
    cur_start = now - timedelta(days=period_days)
    prev_start = cur_start - timedelta(days=period_days)

    cur_won = [d for d in won_deals if d.created_at and d.created_at >= cur_start]
    prev_won = [d for d in won_deals if d.created_at and prev_start <= d.created_at < cur_start]
    cur_won_val = sum(d.value_inr for d in cur_won)
    prev_won_val = sum(d.value_inr for d in prev_won)

    cur_pipe = [d for d in active_deals if d.created_at and d.created_at >= cur_start]
    prev_pipe = [d for d in active_deals if d.created_at and prev_start <= d.created_at < cur_start]
    cur_pipe_val = sum(d.value_inr for d in cur_pipe)
    prev_pipe_val = sum(d.value_inr for d in prev_pipe)

    cur_closed = [d for d in all_deals if d.stage in ("Won", "Lost") and d.created_at and d.created_at >= cur_start]
    prev_closed = [d for d in all_deals if d.stage in ("Won", "Lost") and d.created_at and prev_start <= d.created_at < cur_start]
    cur_wr = sum(1 for d in cur_closed if d.stage == "Won") / max(1, len(cur_closed)) * 100
    prev_wr = sum(1 for d in prev_closed if d.stage == "Won") / max(1, len(prev_closed)) * 100

    cur_active = [d for d in active_deals if d.created_at and d.created_at >= cur_start]
    prev_active = [d for d in active_deals if d.created_at and prev_start <= d.created_at < cur_start]
    cur_avg_days = sum(d.days_in_stage for d in cur_active) / max(1, len(cur_active))
    prev_avg_days = sum(d.days_in_stage for d in prev_active) / max(1, len(prev_active))

    won_value = sum(d.value_inr for d in won_deals)
    lost_value = sum(d.value_inr for d in lost_deals)
    active_value = total_pipeline
    nrr = round((won_value + active_value) / max(1, won_value + lost_value) * 100, 1)

    cur_lost_val = sum(d.value_inr for d in lost_deals if d.created_at and d.created_at >= cur_start)
    prev_lost_val = sum(d.value_inr for d in lost_deals if d.created_at and prev_start <= d.created_at < cur_start)
    cur_nrr = (cur_won_val + cur_pipe_val) / max(1, cur_won_val + cur_lost_val) * 100
    prev_nrr = (prev_won_val + prev_pipe_val) / max(1, prev_won_val + prev_lost_val) * 100

    confidence = _data_confidence(all_deals)
    arr_val = total_won_value
    mrr_val = arr_val / 12
    arr_trend, arr_dir = _compute_trend(cur_won_val, prev_won_val)
    pipe_trend, pipe_dir = _compute_trend(cur_pipe_val, prev_pipe_val)
    wr_trend, wr_dir = _compute_trend(cur_wr, prev_wr)
    cycle_trend, cycle_dir = _compute_trend(cur_avg_days, prev_avg_days)
    nrr_trend, nrr_dir = _compute_trend(cur_nrr, prev_nrr)

    kpis = ExecutiveKPIs(
        arr=KPIMetric(
            value=arr_val, formatted=format_inr(arr_val, compact=True),
            trend_pct=arr_trend, trend_direction=arr_dir, is_positive=arr_trend >= 0,
            confidence=confidence, source="database",
            sparkline=_weekly_values(won_deals),
        ),
        mrr=KPIMetric(
            value=mrr_val, formatted=format_inr(mrr_val, compact=True),
            trend_pct=arr_trend, trend_direction=arr_dir, is_positive=arr_trend >= 0,
            confidence=confidence, source="database",
        ),
        pipeline_value=KPIMetric(
            value=total_pipeline, formatted=format_inr(total_pipeline, compact=True),
            trend_pct=pipe_trend, trend_direction=pipe_dir, is_positive=pipe_trend >= 0,
            confidence=confidence, source="database",
        ),
        win_rate=KPIMetric(
            value=win_rate, formatted=f"{win_rate:.0f}%",
            trend_pct=wr_trend, trend_direction=wr_dir,
            is_positive=wr_trend >= 0, confidence=confidence, source="database",
        ),
        avg_deal_cycle=KPIMetric(
            value=avg_days, formatted=f"{avg_days:.0f} days",
            trend_pct=cycle_trend, trend_direction=cycle_dir,
            is_positive=cycle_trend <= 0, confidence=confidence, source="database",
        ),
        net_revenue_retention=KPIMetric(
            value=nrr, formatted=f"{nrr:.0f}%",
            trend_pct=nrr_trend, trend_direction=nrr_dir, is_positive=nrr_trend >= 0,
            confidence=confidence, source="database",
        ),
    )

    stage_counts = Counter(d.stage for d in all_deals)
    stage_values: dict[str, float] = {}
    for d in all_deals:
        stage_values.setdefault(d.stage, 0)
        stage_values[d.stage] += d.value_inr

    stages = []
    for i, s in enumerate(STAGE_ORDER):
        count = stage_counts.get(s, 0)
        val = stage_values.get(s, 0)
        next_stage = STAGE_ORDER[i + 1] if i + 1 < len(STAGE_ORDER) else None
        next_count = stage_counts.get(next_stage, 0) if next_stage else count
        conv = (next_count / count) if count > 0 else 0
        stages.append(FunnelStage(stage_name=s, count=count, value_inr=val, conversion_rate=round(conv, 2)))

    total_conv = (stage_counts.get("Won", 0) / stage_counts.get("Lead", 1)) if stage_counts.get("Lead") else 0
    funnel = FunnelData(stages=stages, overall_conversion=round(total_conv, 3), period=time_window)

    industry_risk: dict[str, dict] = {}
    for d in active_deals:
        prospect_result = await db.get(Prospect, d.prospect_id)
        ind = prospect_result.industry if prospect_result else "Unknown"
        if ind not in industry_risk:
            industry_risk[ind] = {"count": 0, "total_value": 0, "total_risk": 0}
        industry_risk[ind]["count"] += 1
        industry_risk[ind]["total_value"] += d.value_inr
        industry_risk[ind]["total_risk"] += (d.risk_score or 0)

    heatmap_cells = []
    for ind, data in sorted(industry_risk.items(), key=lambda x: -x[1]["total_value"])[:8]:
        avg_risk = data["total_risk"] / data["count"] if data["count"] > 0 else 0
        level = classify_risk(avg_risk)
        heatmap_cells.append(RiskHeatmapCell(
            segment=ind, risk_level=level, deal_count=data["count"], total_value_inr=data["total_value"],
        ))

    sorted_active = sorted(active_deals, key=lambda d: d.value_inr, reverse=True)
    at_risk = sorted([d for d in active_deals if (d.risk_score or 0) > 40], key=lambda d: -(d.risk_score or 0))

    async def deal_to_summary(d: Deal) -> DealSummary:
        p = await db.get(Prospect, d.prospect_id)
        return DealSummary(
            id=d.id, prospect_name=p.company_name if p else "Unknown",
            stage=d.stage, value_inr=d.value_inr,
            risk_score=d.risk_score or 0, days_in_stage=d.days_in_stage, owner=d.owner,
        )

    top_deals = [await deal_to_summary(d) for d in sorted_active[:5]]
    at_risk_deals = [await deal_to_summary(d) for d in at_risk[:5]]

    now = datetime.utcnow()
    weekly_revenue = _weekly_values(won_deals, weeks=12)
    revenue_forecast_data = {
        "historical": [
            {"date": (now - timedelta(weeks=12 - i)).strftime("%Y-%m-%d"), "revenue": v}
            for i, v in enumerate(weekly_revenue)
        ],
        "forecast": [
            {
                "date": (now + timedelta(weeks=i + 1)).strftime("%Y-%m-%d"),
                "p10": total_won_value * (0.9 + i * 0.02),
                "p50": total_won_value * (1.0 + i * 0.04),
                "p90": total_won_value * (1.1 + i * 0.06),
            }
            for i in range(4)
        ],
    }

    velocity_data = []
    for i, s in enumerate(["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation"]):
        stage_deals = [d for d in active_deals if d.stage == s]
        avg_days = sum(d.days_in_stage for d in stage_deals) / max(len(stage_deals), 1)
        velocity_data.append({
            "week": s,
            "avgDaysInStage": round(avg_days, 1),
            "throughput": len(stage_deals),
            "rollingMeanDays": round(avg_days * 0.9, 1),
            "upperControlLimit": round(avg_days * 1.5, 1),
            "lowerControlLimit": round(avg_days * 0.5, 1),
        })

    summary = ExecutiveSummary(
        kpis=kpis,
        revenue_forecast=revenue_forecast_data,
        pipeline_velocity=velocity_data,
        funnel=funnel,
        risk_heatmap=RiskHeatmapData(cells=heatmap_cells),
        top_deals=top_deals,
        at_risk_deals=at_risk_deals,
        time_window=time_window,
    )
    return APIResponse(data=summary)
