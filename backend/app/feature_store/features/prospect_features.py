"""Prospect feature engineering.

Computes derived features from raw prospect data for use by the scoring
engine and ML models.  Features are designed for the Indian market context.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# Revenue band boundaries in INR
REVENUE_BANDS: list[tuple[str, float, float]] = [
    ("micro", 0, 5e6),
    ("small", 5e6, 5e7),
    ("medium", 5e7, 5e8),
    ("large", 5e8, 5e9),
    ("enterprise", 5e9, float("inf")),
]


def compute_prospect_features(
    prospect_id: str,
    raw_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute a full feature vector for a prospect.

    Parameters
    ----------
    prospect_id : unique prospect identifier
    raw_data : raw prospect attributes (from DB or enrichment).
        If None, features are returned with defaults / NaN markers.
    """
    data = raw_data or {}
    features: dict[str, Any] = {"prospect_id": prospect_id}

    features.update(_compute_size_features(data))
    features.update(_compute_industry_features(data))
    features.update(_compute_growth_features(data))
    features.update(_compute_financial_features(data))
    features.update(_compute_registration_features(data))
    features.update(_compute_engagement_features(data))
    features.update(_compute_geographic_features(data))

    features["feature_completeness"] = _compute_completeness(features)

    return features


# ── Feature groups ───────────────────────────────────────────────────────────

def _compute_size_features(data: dict[str, Any]) -> dict[str, Any]:
    revenue = data.get("revenue_inr")
    employees = data.get("employee_count")

    features: dict[str, Any] = {
        "revenue_inr": revenue,
        "revenue_log": math.log1p(revenue) if revenue and revenue > 0 else None,
        "employee_count": employees,
        "employee_log": math.log1p(employees) if employees and employees > 0 else None,
        "revenue_band": None,
        "revenue_per_employee": None,
    }

    if revenue is not None:
        for band_name, lo, hi in REVENUE_BANDS:
            if lo <= revenue < hi:
                features["revenue_band"] = band_name
                break

    if revenue and employees and employees > 0:
        features["revenue_per_employee"] = revenue / employees

    return features


def _compute_industry_features(data: dict[str, Any]) -> dict[str, Any]:
    nic_code = data.get("nic_code", "")
    return {
        "nic_code": nic_code,
        "nic_section": nic_code[:1] if nic_code else None,
        "nic_division": nic_code[:2] if len(nic_code) >= 2 else None,
        "nic_group": nic_code[:3] if len(nic_code) >= 3 else None,
        "industry": data.get("industry"),
        "is_tech_sector": nic_code[:2] in ("62", "63") if len(nic_code) >= 2 else False,
        "is_financial_sector": nic_code[:2] in ("64", "65", "66") if len(nic_code) >= 2 else False,
    }


def _compute_growth_features(data: dict[str, Any]) -> dict[str, Any]:
    rev_growth = data.get("revenue_growth_pct")
    hiring_growth = data.get("hiring_growth_pct")
    funding = data.get("recent_funding_inr")

    has_growth = any(v is not None and v > 0 for v in [rev_growth, hiring_growth, funding])

    return {
        "revenue_growth_pct": rev_growth,
        "hiring_growth_pct": hiring_growth,
        "recent_funding_inr": funding,
        "recent_funding_log": math.log1p(funding) if funding and funding > 0 else None,
        "has_positive_growth_signal": has_growth,
        "growth_composite": _safe_mean([
            _normalise(rev_growth, -20, 60) if rev_growth is not None else None,
            _normalise(hiring_growth, -10, 50) if hiring_growth is not None else None,
            _normalise(math.log1p(funding) if funding else 0, 0, math.log1p(5e9)) if funding else None,
        ]),
    }


def _compute_financial_features(data: dict[str, Any]) -> dict[str, Any]:
    margin = data.get("profit_margin_pct")
    de_ratio = data.get("debt_equity_ratio")
    current = data.get("current_ratio")
    roe = data.get("roe_pct")

    return {
        "profit_margin_pct": margin,
        "debt_equity_ratio": de_ratio,
        "current_ratio": current,
        "roe_pct": roe,
        "is_profitable": (margin is not None and margin > 0),
        "is_overleveraged": (de_ratio is not None and de_ratio > 2.0),
        "financial_health_composite": _safe_mean([
            _normalise(margin, -10, 30) if margin is not None else None,
            1.0 - _normalise(de_ratio, 0, 3) if de_ratio is not None else None,
            _normalise(current, 0, 3) if current is not None else None,
            _normalise(roe, -10, 30) if roe is not None else None,
        ]),
    }


def _compute_registration_features(data: dict[str, Any]) -> dict[str, Any]:
    mca_date = data.get("mca_registration_date")
    gst_freq = data.get("gst_filing_frequency")
    dpiit = data.get("dpiit_recognized", False)
    listed = data.get("listed_exchange")

    company_age_years = None
    if mca_date:
        if isinstance(mca_date, str):
            try:
                mca_date = datetime.fromisoformat(mca_date)
            except ValueError:
                mca_date = None
        if isinstance(mca_date, datetime):
            company_age_years = (datetime.utcnow() - mca_date).days / 365.25

    gst_score_map = {"monthly": 1.0, "quarterly": 0.7, "annual": 0.4}

    return {
        "has_mca_registration": mca_date is not None,
        "company_age_years": round(company_age_years, 2) if company_age_years else None,
        "gst_filing_frequency": gst_freq,
        "gst_compliance_score": gst_score_map.get((gst_freq or "").lower(), 0.0),
        "dpiit_recognized": dpiit,
        "is_listed": listed is not None and listed != "",
        "listed_exchange": listed,
    }


def _compute_engagement_features(data: dict[str, Any]) -> dict[str, Any]:
    visits = data.get("website_visits_30d")
    downloads = data.get("content_downloads_30d")

    return {
        "website_visits_30d": visits,
        "content_downloads_30d": downloads,
        "has_engagement": (visits is not None and visits > 0) or (downloads is not None and downloads > 0),
        "engagement_composite": _safe_mean([
            _normalise(visits, 0, 100) if visits is not None else None,
            _normalise(downloads, 0, 20) if downloads is not None else None,
        ]),
    }


def _compute_geographic_features(data: dict[str, Any]) -> dict[str, Any]:
    state = data.get("state")
    city = data.get("city")
    tier1_states = {"MH", "KA", "DL", "TN", "TG"}
    tier2_states = {"GJ", "HR", "UP", "WB", "RJ", "KL", "AP", "MP"}

    state_upper = (state or "").upper().strip()

    return {
        "state": state,
        "city": city,
        "is_tier1_state": state_upper in tier1_states,
        "is_tier2_state": state_upper in tier2_states,
        "is_metro": state_upper in tier1_states,
    }


# ── Utility functions ────────────────────────────────────────────────────────

def _normalise(value: float, min_val: float, max_val: float) -> float:
    if max_val <= min_val:
        return 0.0
    return min(max((value - min_val) / (max_val - min_val), 0.0), 1.0)


def _safe_mean(values: list[float | None]) -> float | None:
    filtered = [v for v in values if v is not None]
    if not filtered:
        return None
    return round(sum(filtered) / len(filtered), 4)


def _compute_completeness(features: dict[str, Any]) -> float:
    """Fraction of non-metadata features that have a non-None value."""
    meta_keys = {"prospect_id", "feature_completeness"}
    total = 0
    present = 0
    for k, v in features.items():
        if k in meta_keys or k.startswith("_"):
            continue
        total += 1
        if v is not None:
            present += 1
    return round(present / total, 4) if total > 0 else 0.0
