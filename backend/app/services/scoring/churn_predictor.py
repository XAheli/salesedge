"""Churn prediction engine.

Implements the logistic model from Section 9.3::

    P(churn in next 90d | X) = σ(β·X)

Uses scikit-learn's LogisticRegression with Platt scaling for calibrated
probability estimates.  Falls back to a heuristic model when no trained
model is available.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import numpy as np

try:
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression

    _SKLEARN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SKLEARN_AVAILABLE = False


FEATURE_NAMES: list[str] = [
    "usage_trend_30d",
    "support_ticket_frequency",
    "nps_score",
    "payment_delays",
    "champion_turnover",
    "competitive_mentions",
    "contract_renewal_proximity",
    "macro_headwind",
]

RISK_THRESHOLDS: dict[str, tuple[float, float]] = {
    "critical": (0.75, 1.0),
    "high": (0.50, 0.75),
    "medium": (0.25, 0.50),
    "low": (0.0, 0.25),
}

# Default coefficients when no trained model is available (hand-tuned)
DEFAULT_COEFFICIENTS: dict[str, float] = {
    "usage_trend_30d": -0.8,
    "support_ticket_frequency": 0.6,
    "nps_score": -0.5,
    "payment_delays": 0.7,
    "champion_turnover": 0.9,
    "competitive_mentions": 0.4,
    "contract_renewal_proximity": 0.3,
    "macro_headwind": 0.2,
}
DEFAULT_INTERCEPT: float = -0.5


@dataclass
class CustomerData:
    """Input features for churn prediction."""

    customer_id: str
    company_name: str
    usage_trend_30d: float = 0.0        # normalised -1 (declining) to 1 (growing)
    support_ticket_frequency: float = 0.0  # tickets per week
    nps_score: float = 0.0              # -100 to 100 mapped to -1..1
    payment_delays: float = 0.0          # count of late payments in last 90d
    champion_turnover: float = 0.0       # 0 or 1 (binary: champion left?)
    competitive_mentions: float = 0.0    # count in last 30d
    contract_renewal_proximity: float = 0.0  # days until renewal / 365
    macro_headwind: float = 0.0          # composite macro risk 0..1


@dataclass
class ChurnPrediction:
    """Output of the churn prediction engine."""

    customer_id: str
    company_name: str
    probability: float
    risk_level: str
    contributing_factors: list[tuple[str, float]]
    confidence_interval: tuple[float, float]
    predicted_at: datetime = field(default_factory=datetime.utcnow)


class ChurnPredictor:
    """Predict 90-day churn probability for existing customers.

    When a trained sklearn model is supplied, it is used with Platt-calibrated
    probabilities.  Otherwise a heuristic logistic model with default
    coefficients is applied.
    """

    def __init__(
        self,
        model: Any | None = None,
        coefficients: dict[str, float] | None = None,
        intercept: float | None = None,
    ) -> None:
        self._trained_model = model
        self._coefs = coefficients or DEFAULT_COEFFICIENTS.copy()
        self._intercept = intercept if intercept is not None else DEFAULT_INTERCEPT

    # ── Public API ───────────────────────────────────────────────────────

    def predict(self, customer: CustomerData) -> ChurnPrediction:
        """Predict churn for a single customer."""
        features = self._extract_features(customer)

        if self._trained_model is not None and _SKLEARN_AVAILABLE:
            prob = self._predict_with_model(features)
        else:
            prob = self._predict_heuristic(features)

        prob = min(max(prob, 0.0), 1.0)
        risk_level = self._classify_risk(prob)
        factors = self._compute_contributions(features)
        ci = self._compute_ci(prob, n_features=len(features))

        return ChurnPrediction(
            customer_id=customer.customer_id,
            company_name=customer.company_name,
            probability=round(prob, 4),
            risk_level=risk_level,
            contributing_factors=factors,
            confidence_interval=(round(ci[0], 4), round(ci[1], 4)),
        )

    def predict_batch(self, customers: list[CustomerData]) -> list[ChurnPrediction]:
        """Predict churn for a batch of customers."""
        return [self.predict(c) for c in customers]

    def fit(
        self,
        X: np.ndarray,
        y: np.ndarray,
        calibrate: bool = True,
        cv: int = 5,
    ) -> None:
        """Train the underlying logistic model on labelled data.

        Parameters
        ----------
        X : array of shape (n_samples, 8)
        y : binary array (1 = churned)
        calibrate : apply Platt scaling via CalibratedClassifierCV
        cv : cross-validation folds for calibration
        """
        if not _SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is required for model training")

        base = LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            class_weight="balanced",
        )
        if calibrate:
            self._trained_model = CalibratedClassifierCV(
                base, method="sigmoid", cv=cv,
            )
        else:
            self._trained_model = base

        self._trained_model.fit(X, y)

    # ── Private helpers ──────────────────────────────────────────────────

    def _extract_features(self, customer: CustomerData) -> dict[str, float]:
        return {name: getattr(customer, name, 0.0) for name in FEATURE_NAMES}

    def _predict_with_model(self, features: dict[str, float]) -> float:
        X = np.array([[features[n] for n in FEATURE_NAMES]])
        probs = self._trained_model.predict_proba(X)
        return float(probs[0, 1])

    def _predict_heuristic(self, features: dict[str, float]) -> float:
        """Sigmoid of the linear combination using default coefficients."""
        z = self._intercept + sum(
            self._coefs.get(name, 0.0) * val for name, val in features.items()
        )
        return 1.0 / (1.0 + math.exp(-z))

    def _compute_contributions(
        self, features: dict[str, float],
    ) -> list[tuple[str, float]]:
        contribs = [
            (name, round(self._coefs.get(name, 0.0) * val, 4))
            for name, val in features.items()
        ]
        contribs.sort(key=lambda x: abs(x[1]), reverse=True)
        return contribs

    @staticmethod
    def _classify_risk(probability: float) -> str:
        for level, (lo, hi) in RISK_THRESHOLDS.items():
            if lo <= probability < hi:
                return level
        return "critical" if probability >= 0.75 else "low"

    @staticmethod
    def _compute_ci(
        prob: float,
        n_features: int,
        z: float = 1.96,
    ) -> tuple[float, float]:
        """Approximate confidence interval using the Wald method."""
        se = math.sqrt(prob * (1 - prob) / max(n_features, 1))
        lower = max(prob - z * se, 0.0)
        upper = min(prob + z * se, 1.0)
        return (lower, upper)
