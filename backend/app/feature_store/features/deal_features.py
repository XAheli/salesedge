"""Deal feature engineering.

Computes derived features from deal pipeline data for use by the risk
scoring engine and ML models.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Expected days per stage (Indian enterprise sales cycle)
EXPECTED_STAGE_DAYS: dict[str, int] = {
    "discovery": 10,
    "qualification": 14,
    "proposal": 21,
    "negotiation": 28,
    "verbal_commit": 14,
    "procurement": 30,
}


def compute_deal_features(
    deal_id: str,
    raw_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute a full feature vector for a deal.

    Parameters
    ----------
    deal_id : unique deal identifier
    raw_data : raw deal attributes (from DB / CRM)
    """
    data = raw_data or {}
    features: dict[str, Any] = {"deal_id": deal_id}

    features.update(_compute_value_features(data))
    features.update(_compute_velocity_features(data))
    features.update(_compute_engagement_features(data))
    features.update(_compute_stakeholder_features(data))
    features.update(_compute_competitive_features(data))
    features.update(_compute_sentiment_features(data))

    features["feature_completeness"] = _compute_completeness(features)

    return features


def _compute_value_features(data: dict[str, Any]) -> dict[str, Any]:
    current = data.get("value_inr", 0)
    initial = data.get("initial_value_inr")

    value_drift = None
    if initial and initial > 0:
        value_drift = (current - initial) / initial

    return {
        "value_inr": current,
        "value_log": math.log1p(current) if current > 0 else 0.0,
        "initial_value_inr": initial,
        "value_drift_ratio": round(value_drift, 4) if value_drift is not None else None,
        "is_value_increasing": value_drift is not None and value_drift > 0,
        "is_large_deal": current > 5e7,  # > 50 lakhs
    }


def _compute_velocity_features(data: dict[str, Any]) -> dict[str, Any]:
    stage = data.get("stage", "").lower()
    days_in_stage = data.get("days_in_stage", 0)
    expected = EXPECTED_STAGE_DAYS.get(stage, 14)

    velocity_ratio = days_in_stage / expected if expected > 0 else 0

    total_days = data.get("total_days_in_pipeline", 0)
    expected_close = data.get("expected_close_date")
    days_to_close = None
    if expected_close:
        if isinstance(expected_close, str):
            try:
                expected_close = datetime.fromisoformat(expected_close)
            except ValueError:
                expected_close = None
        if isinstance(expected_close, datetime):
            days_to_close = (expected_close - datetime.utcnow()).days

    return {
        "stage": stage,
        "days_in_stage": days_in_stage,
        "expected_stage_days": expected,
        "stage_velocity_ratio": round(velocity_ratio, 4),
        "is_stalled": velocity_ratio > 1.5,
        "is_overdue": velocity_ratio > 2.0,
        "total_pipeline_days": total_days,
        "days_to_expected_close": days_to_close,
    }


def _compute_engagement_features(data: dict[str, Any]) -> dict[str, Any]:
    events = data.get("events", [])
    window = data.get("analysis_window_days", 14)
    baseline = data.get("baseline_event_rate", 1.0)

    recent_rate = len(events) / window if window > 0 else 0
    momentum = recent_rate / baseline if baseline > 0 else 0

    events_7d = data.get("engagement_events_7d", 0)
    events_30d = data.get("engagement_events_30d", len(events))

    return {
        "recent_event_count": len(events),
        "recent_event_rate": round(recent_rate, 4),
        "engagement_momentum": round(min(momentum, 2.0), 4),
        "engagement_events_7d": events_7d,
        "engagement_events_30d": events_30d,
        "is_engagement_declining": momentum < 0.5,
        "is_engagement_strong": momentum >= 1.0,
        "days_since_last_activity": data.get("days_since_last_activity"),
    }


def _compute_stakeholder_features(data: dict[str, Any]) -> dict[str, Any]:
    interactions: dict[str, int] = data.get("stakeholder_interactions", {})
    total_dm = max(data.get("total_decision_makers", 1), 1)
    engaged = len(interactions)

    coverage = min(engaged / total_dm, 1.0)

    entropy = 0.0
    total_interactions = sum(interactions.values())
    if total_interactions > 0 and len(interactions) > 1:
        for count in interactions.values():
            if count > 0:
                p = count / total_interactions
                entropy -= p * math.log2(p)
        max_entropy = math.log2(len(interactions))
        entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    return {
        "stakeholders_engaged": engaged,
        "total_decision_makers": total_dm,
        "stakeholder_coverage": round(coverage, 4),
        "stakeholder_entropy": round(entropy, 4),
        "is_single_threaded": engaged <= 1,
        "has_champion": data.get("champion_exists", False),
        "has_executive_sponsor": data.get("executive_sponsor", False),
    }


def _compute_competitive_features(data: dict[str, Any]) -> dict[str, Any]:
    mentions = data.get("competitor_mentions", 0)
    competitors = data.get("active_competitors", [])

    return {
        "competitor_mention_count": mentions,
        "active_competitor_count": len(competitors),
        "has_competitive_pressure": mentions > 0 or len(competitors) > 0,
        "competitor_intensity": round(1.0 - 1.0 / (1.0 + mentions), 4),
    }


def _compute_sentiment_features(data: dict[str, Any]) -> dict[str, Any]:
    scores = data.get("sentiment_scores", [])

    if not scores:
        return {
            "avg_sentiment": None,
            "sentiment_trend": None,
            "is_sentiment_negative": False,
            "sentiment_volatility": None,
        }

    avg = sum(scores) / len(scores)

    trend = None
    if len(scores) >= 4:
        first_half = scores[: len(scores) // 2]
        second_half = scores[len(scores) // 2 :]
        trend = (sum(second_half) / len(second_half)) - (sum(first_half) / len(first_half))

    volatility = None
    if len(scores) >= 2:
        mean = avg
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        volatility = math.sqrt(variance)

    return {
        "avg_sentiment": round(avg, 4),
        "sentiment_trend": round(trend, 4) if trend is not None else None,
        "is_sentiment_negative": avg < -0.2,
        "sentiment_volatility": round(volatility, 4) if volatility is not None else None,
    }


def _compute_completeness(features: dict[str, Any]) -> float:
    meta_keys = {"deal_id", "feature_completeness"}
    total = 0
    present = 0
    for k, v in features.items():
        if k in meta_keys or k.startswith("_"):
            continue
        total += 1
        if v is not None:
            present += 1
    return round(present / total, 4) if total > 0 else 0.0
