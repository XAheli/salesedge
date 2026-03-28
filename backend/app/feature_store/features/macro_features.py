"""Macro-economic feature engineering.

Computes features from government and macro-economic data sources (RBI,
MOSPI, CSO) for use as contextual signals in scoring models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


def compute_macro_features(
    sector: str | None = None,
    state: str | None = None,
    raw_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute a macro-economic feature vector.

    Parameters
    ----------
    sector : NIC division or industry label (e.g. "62", "IT")
    state : 2-letter state code (e.g. "MH")
    raw_data : pre-fetched macro indicators from data sources
    """
    data = raw_data or {}
    features: dict[str, Any] = {
        "sector": sector,
        "state": state,
        "computed_at": datetime.utcnow().isoformat(),
    }

    features.update(_compute_gdp_features(data))
    features.update(_compute_inflation_features(data))
    features.update(_compute_interest_rate_features(data))
    features.update(_compute_trade_features(data))
    features.update(_compute_policy_features(data, sector, state))
    features.update(_compute_sector_features(data, sector))
    features.update(_compute_state_features(data, state))

    features["macro_headwind_score"] = _compute_headwind_composite(features)

    return features


# ── Feature groups ───────────────────────────────────────────────────────────

def _compute_gdp_features(data: dict[str, Any]) -> dict[str, Any]:
    gdp_growth = data.get("gdp_growth_pct")
    gdp_prev = data.get("gdp_growth_prev_quarter_pct")

    trend = None
    if gdp_growth is not None and gdp_prev is not None:
        trend = gdp_growth - gdp_prev

    return {
        "gdp_growth_pct": gdp_growth,
        "gdp_growth_trend": round(trend, 4) if trend is not None else None,
        "is_gdp_accelerating": trend is not None and trend > 0,
    }


def _compute_inflation_features(data: dict[str, Any]) -> dict[str, Any]:
    cpi = data.get("cpi_inflation_pct")
    wpi = data.get("wpi_inflation_pct")

    rbi_target_upper = 6.0

    return {
        "cpi_inflation_pct": cpi,
        "wpi_inflation_pct": wpi,
        "is_inflation_elevated": cpi is not None and cpi > rbi_target_upper,
        "inflation_spread": round(cpi - wpi, 4) if cpi is not None and wpi is not None else None,
    }


def _compute_interest_rate_features(data: dict[str, Any]) -> dict[str, Any]:
    repo = data.get("repo_rate_pct")
    repo_prev = data.get("repo_rate_prev_pct")
    crr = data.get("crr_pct")

    rate_direction = None
    if repo is not None and repo_prev is not None:
        if repo > repo_prev:
            rate_direction = "tightening"
        elif repo < repo_prev:
            rate_direction = "easing"
        else:
            rate_direction = "unchanged"

    return {
        "repo_rate_pct": repo,
        "crr_pct": crr,
        "monetary_policy_direction": rate_direction,
        "is_rate_tightening": rate_direction == "tightening",
    }


def _compute_trade_features(data: dict[str, Any]) -> dict[str, Any]:
    exports = data.get("merchandise_exports_usd_bn")
    imports = data.get("merchandise_imports_usd_bn")
    fdi = data.get("fdi_inflow_usd_bn")

    trade_balance = None
    if exports is not None and imports is not None:
        trade_balance = exports - imports

    return {
        "merchandise_exports_usd_bn": exports,
        "merchandise_imports_usd_bn": imports,
        "trade_balance_usd_bn": round(trade_balance, 4) if trade_balance is not None else None,
        "fdi_inflow_usd_bn": fdi,
        "is_trade_surplus": trade_balance is not None and trade_balance > 0,
    }


def _compute_policy_features(
    data: dict[str, Any],
    sector: str | None,
    state: str | None,
) -> dict[str, Any]:
    policies = data.get("active_policies", [])

    relevant = [
        p for p in policies
        if (sector and sector.lower() in [s.lower() for s in p.get("affected_sectors", [])])
        or (state and state.upper() in [s.upper() for s in p.get("affected_states", [])])
    ]

    positive = sum(1 for p in relevant if p.get("impact") == "positive")
    negative = sum(1 for p in relevant if p.get("impact") == "negative")

    favorability = 0.5
    if relevant:
        favorability = positive / len(relevant)

    return {
        "relevant_policy_count": len(relevant),
        "positive_policy_count": positive,
        "negative_policy_count": negative,
        "regulatory_favorability": round(favorability, 4),
    }


def _compute_sector_features(
    data: dict[str, Any],
    sector: str | None,
) -> dict[str, Any]:
    sector_data = data.get("sector_indicators", {}).get(sector, {}) if sector else {}

    return {
        "sector_iip_growth_pct": sector_data.get("iip_growth_pct"),
        "sector_credit_growth_pct": sector_data.get("credit_growth_pct"),
        "sector_pmi": sector_data.get("pmi"),
        "sector_is_expanding": (
            sector_data.get("pmi") is not None and sector_data["pmi"] > 50
        ),
    }


def _compute_state_features(
    data: dict[str, Any],
    state: str | None,
) -> dict[str, Any]:
    state_data = data.get("state_indicators", {}).get(state, {}) if state else {}

    return {
        "state_gsdp_growth_pct": state_data.get("gsdp_growth_pct"),
        "state_ease_of_business_rank": state_data.get("ease_of_business_rank"),
        "state_industrial_investment_inr_cr": state_data.get("industrial_investment_inr_cr"),
    }


def _compute_headwind_composite(features: dict[str, Any]) -> float:
    """Compute a composite macro headwind score in [0, 1].

    Higher = more headwinds (bad for sales).
    """
    signals: list[float] = []

    gdp = features.get("gdp_growth_pct")
    if gdp is not None:
        signals.append(max(0, 1.0 - gdp / 8.0))

    if features.get("is_inflation_elevated"):
        signals.append(0.7)
    elif features.get("cpi_inflation_pct") is not None:
        signals.append(min(features["cpi_inflation_pct"] / 10.0, 1.0))

    if features.get("is_rate_tightening"):
        signals.append(0.6)
    elif features.get("monetary_policy_direction") == "easing":
        signals.append(0.2)

    favorability = features.get("regulatory_favorability")
    if favorability is not None:
        signals.append(1.0 - favorability)

    if not signals:
        return 0.5

    return round(sum(signals) / len(signals), 4)
