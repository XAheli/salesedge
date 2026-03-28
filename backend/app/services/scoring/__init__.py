from __future__ import annotations

from app.services.scoring.calibration import (
    compute_brier_score,
    compute_calibration_curve,
    compute_calibration_loss,
    platt_scaling,
)
from app.services.scoring.churn_predictor import ChurnPredictor
from app.services.scoring.deal_risk_scorer import DealRiskScorer
from app.services.scoring.explainability import (
    compute_shap_values,
    generate_explanation,
    get_top_contributors,
)
from app.services.scoring.prospect_scorer import ProspectScorer
from app.services.scoring.recovery_prioritizer import RecoveryPrioritizer

__all__ = [
    "ProspectScorer",
    "DealRiskScorer",
    "ChurnPredictor",
    "RecoveryPrioritizer",
    "platt_scaling",
    "compute_calibration_curve",
    "compute_brier_score",
    "compute_calibration_loss",
    "compute_shap_values",
    "generate_explanation",
    "get_top_contributors",
]
