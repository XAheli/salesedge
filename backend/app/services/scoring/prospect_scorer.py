"""Prospect Fit Score engine.

Implements the weighted-sum scoring formula from Section 9.1::

    FitScore(p) = Σᵢ wᵢ · normalize(fᵢ(p))

Features are normalised to [0, 1] then combined with configurable weights.
Indian-specific signals (NIC codes, MCA registration, GST filings, DPIIT
recognition) are first-class features.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class ProspectData:
    """Raw prospect data consumed by the scoring engine."""

    company_name: str
    revenue_inr: float | None = None
    employee_count: int | None = None
    industry: str | None = None
    nic_code: str | None = None
    state: str | None = None
    city: str | None = None
    tech_stack: list[str] = field(default_factory=list)
    revenue_growth_pct: float | None = None
    hiring_growth_pct: float | None = None
    recent_funding_inr: float | None = None
    website_visits_30d: int | None = None
    content_downloads_30d: int | None = None
    mca_registration_date: datetime | None = None
    gst_filing_frequency: str | None = None  # monthly, quarterly, annual
    dpiit_recognized: bool = False
    profit_margin_pct: float | None = None
    debt_equity_ratio: float | None = None
    regulatory_favorability: float | None = None  # pre-computed 0-1
    listed_exchange: str | None = None


@dataclass
class FeatureContribution:
    """Individual feature's contribution to the final score."""

    feature_name: str
    raw_value: Any
    normalised_value: float
    weight: float
    weighted_contribution: float


@dataclass
class ScoringResult:
    """Output of the prospect scoring engine."""

    score: float
    confidence: float
    feature_contributions: list[FeatureContribution]
    explanation: str
    scored_at: datetime = field(default_factory=datetime.utcnow)


# ─── Constants ───────────────────────────────────────────────────────────────

DEFAULT_WEIGHTS: dict[str, float] = {
    "company_size_fit": 0.15,
    "industry_fit": 0.15,
    "technology_fit": 0.10,
    "growth_signal": 0.15,
    "engagement_signal": 0.10,
    "geographic_fit": 0.05,
    "regulatory_tailwind": 0.10,
    "financial_health": 0.10,
    "indian_registration": 0.10,
}

TARGET_REVENUE_BANDS_INR: list[tuple[float, float]] = [
    (1e7, 5e7),      # 1 Cr – 5 Cr
    (5e7, 5e8),      # 5 Cr – 50 Cr
    (5e8, 5e9),      # 50 Cr – 500 Cr
]

TARGET_INDUSTRIES_NIC: set[str] = {
    "62",  # Computer programming, consultancy
    "63",  # Information service activities
    "64",  # Financial service activities
    "65",  # Insurance, reinsurance, pension funding
    "26",  # Manufacture of electronic products
    "21",  # Manufacture of pharmaceuticals
}

TARGET_TECH_KEYWORDS: set[str] = {
    "python", "java", "kubernetes", "aws", "azure", "gcp",
    "react", "salesforce", "sap", "oracle", "erp", "crm",
}

TARGET_STATES: set[str] = {
    "MH", "KA", "DL", "TN", "TG", "GJ", "HR", "UP", "WB", "RJ",
}


class ProspectScorer:
    """Score prospects for ICP fit using a weighted multi-feature model."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        total = sum(self.weights.values())
        if not math.isclose(total, 1.0, rel_tol=1e-3):
            self.weights = {k: v / total for k, v in self.weights.items()}

    def score(self, prospect: ProspectData) -> ScoringResult:
        """Score a single prospect and return a detailed result."""
        evaluators: dict[str, tuple[float, Any]] = {
            "company_size_fit": (self._score_company_size(prospect), prospect.revenue_inr),
            "industry_fit": (self._score_industry(prospect), prospect.nic_code),
            "technology_fit": (self._score_technology(prospect), prospect.tech_stack),
            "growth_signal": (self._score_growth(prospect), prospect.revenue_growth_pct),
            "engagement_signal": (self._score_engagement(prospect), prospect.website_visits_30d),
            "geographic_fit": (self._score_geography(prospect), prospect.state),
            "regulatory_tailwind": (self._score_regulatory(prospect), prospect.regulatory_favorability),
            "financial_health": (self._score_financial(prospect), prospect.profit_margin_pct),
            "indian_registration": (self._score_indian_registration(prospect), prospect.dpiit_recognized),
        }

        contributions: list[FeatureContribution] = []
        weighted_sum = 0.0
        completeness: dict[str, bool] = {}

        for feat_name, (norm_val, raw_val) in evaluators.items():
            w = self.weights.get(feat_name, 0.0)
            wc = w * norm_val
            weighted_sum += wc
            contributions.append(FeatureContribution(
                feature_name=feat_name,
                raw_value=raw_val,
                normalised_value=round(norm_val, 4),
                weight=w,
                weighted_contribution=round(wc, 4),
            ))
            completeness[feat_name] = raw_val is not None and raw_val != [] and raw_val != 0

        score_0_100 = round(min(max(weighted_sum * 100, 0.0), 100.0), 2)
        confidence = self._compute_confidence(completeness)
        explanation = self._build_explanation(contributions, score_0_100)

        return ScoringResult(
            score=score_0_100,
            confidence=round(confidence, 4),
            feature_contributions=contributions,
            explanation=explanation,
        )

    def batch_score(self, prospects: list[ProspectData]) -> list[ScoringResult]:
        """Score multiple prospects."""
        return [self.score(p) for p in prospects]

    # ── Feature scorers ──────────────────────────────────────────────────

    def _score_company_size(self, p: ProspectData) -> float:
        if p.revenue_inr is None:
            return 0.0
        best = 0.0
        for lo, hi in TARGET_REVENUE_BANDS_INR:
            if lo <= p.revenue_inr <= hi:
                return 1.0
            distance = min(abs(p.revenue_inr - lo), abs(p.revenue_inr - hi))
            band_width = hi - lo
            best = max(best, max(0.0, 1.0 - distance / band_width))
        return best

    def _score_industry(self, p: ProspectData) -> float:
        if not p.nic_code:
            return 0.0
        division = p.nic_code[:2]
        if division in TARGET_INDUSTRIES_NIC:
            return 1.0
        section = p.nic_code[:1]
        if any(nic.startswith(section) for nic in TARGET_INDUSTRIES_NIC):
            return 0.4
        return 0.0

    def _score_technology(self, p: ProspectData) -> float:
        if not p.tech_stack:
            return 0.0
        matches = sum(1 for t in p.tech_stack if t.lower() in TARGET_TECH_KEYWORDS)
        return self._normalize(matches, 0, max(len(TARGET_TECH_KEYWORDS) / 2, 1))

    def _score_growth(self, p: ProspectData) -> float:
        signals: list[float] = []
        if p.revenue_growth_pct is not None:
            signals.append(self._normalize(p.revenue_growth_pct, -10, 50))
        if p.hiring_growth_pct is not None:
            signals.append(self._normalize(p.hiring_growth_pct, -5, 40))
        if p.recent_funding_inr is not None:
            signals.append(self._normalize(p.recent_funding_inr, 0, 5e9))
        return sum(signals) / len(signals) if signals else 0.0

    def _score_engagement(self, p: ProspectData) -> float:
        signals: list[float] = []
        if p.website_visits_30d is not None:
            signals.append(self._normalize(p.website_visits_30d, 0, 100))
        if p.content_downloads_30d is not None:
            signals.append(self._normalize(p.content_downloads_30d, 0, 20))
        return sum(signals) / len(signals) if signals else 0.0

    def _score_geography(self, p: ProspectData) -> float:
        if not p.state:
            return 0.0
        code = p.state.upper().strip()
        return 1.0 if code in TARGET_STATES else 0.2

    def _score_regulatory(self, p: ProspectData) -> float:
        if p.regulatory_favorability is not None:
            return min(max(p.regulatory_favorability, 0.0), 1.0)
        return 0.5  # neutral default

    def _score_financial(self, p: ProspectData) -> float:
        signals: list[float] = []
        if p.profit_margin_pct is not None:
            signals.append(self._normalize(p.profit_margin_pct, -5, 30))
        if p.debt_equity_ratio is not None:
            signals.append(1.0 - self._normalize(p.debt_equity_ratio, 0, 3))
        return sum(signals) / len(signals) if signals else 0.0

    def _score_indian_registration(self, p: ProspectData) -> float:
        score = 0.0
        if p.mca_registration_date is not None:
            score += 0.3
        if p.gst_filing_frequency:
            freq_scores = {"monthly": 1.0, "quarterly": 0.7, "annual": 0.4}
            score += 0.3 * freq_scores.get(p.gst_filing_frequency.lower(), 0.2)
        if p.dpiit_recognized:
            score += 0.2
        if p.listed_exchange:
            score += 0.2
        return min(score, 1.0)

    # ── Utilities ────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(value: float, min_val: float, max_val: float) -> float:
        """Normalise a value to [0, 1] using min-max scaling."""
        if max_val <= min_val:
            return 0.0
        return min(max((value - min_val) / (max_val - min_val), 0.0), 1.0)

    @staticmethod
    def _compute_confidence(feature_completeness: dict[str, bool]) -> float:
        """Confidence = fraction of features with available data, with a floor."""
        if not feature_completeness:
            return 0.0
        available = sum(1 for v in feature_completeness.values() if v)
        raw = available / len(feature_completeness)
        return max(raw, 0.1)

    @staticmethod
    def _build_explanation(
        contributions: list[FeatureContribution],
        score: float,
    ) -> str:
        sorted_contribs = sorted(
            contributions, key=lambda c: c.weighted_contribution, reverse=True
        )
        top = sorted_contribs[:3]
        parts = [f"Fit score: {score}/100."]
        parts.append("Top drivers: " + ", ".join(
            f"{c.feature_name} ({c.weighted_contribution:.2f})" for c in top
        ))
        missing = [c.feature_name for c in contributions if c.raw_value is None]
        if missing:
            parts.append(f"Missing data for: {', '.join(missing)}.")
        return " ".join(parts)
