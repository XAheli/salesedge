"""SHAP-based model explainability utilities.

Wraps the SHAP library to provide human-readable explanations of model
predictions.  Falls back to a coefficient-based explanation when SHAP is
not available.
"""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    import shap

    _SHAP_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SHAP_AVAILABLE = False


def compute_shap_values(
    model: Any,
    X: np.ndarray,
    feature_names: list[str],
    max_samples: int = 100,
) -> dict[str, float]:
    """Compute mean absolute SHAP values per feature.

    Parameters
    ----------
    model : fitted estimator with ``predict`` or ``predict_proba``
    X : array of shape (n_samples, n_features)
    feature_names : names corresponding to columns of X
    max_samples : background-data size for the SHAP explainer

    Returns
    -------
    Mapping of feature name to mean |SHAP value|.
    """
    if not _SHAP_AVAILABLE:
        return _fallback_importance(model, feature_names)

    background = X if len(X) <= max_samples else shap.sample(X, max_samples)
    explainer = shap.Explainer(model, background, feature_names=feature_names)
    shap_values = explainer(X)

    vals = np.abs(shap_values.values)
    if vals.ndim == 3:
        vals = vals[:, :, 1]
    mean_abs = vals.mean(axis=0)

    return {name: round(float(v), 6) for name, v in zip(feature_names, mean_abs)}


def generate_explanation(
    shap_values: dict[str, float],
    feature_names: list[str],
    top_n: int = 5,
) -> str:
    """Generate a human-readable explanation from SHAP values.

    Parameters
    ----------
    shap_values : output of ``compute_shap_values``
    feature_names : ordered list of all feature names
    top_n : how many top features to highlight
    """
    top = get_top_contributors(shap_values, n=top_n)

    if not top:
        return "Insufficient data to generate an explanation."

    lines = ["This prediction is primarily driven by:"]
    for rank, (name, value) in enumerate(top, start=1):
        direction = "increases" if value > 0 else "decreases"
        lines.append(
            f"  {rank}. {_humanise_feature(name)} — {direction} the score "
            f"(impact: {abs(value):.4f})"
        )

    total_impact = sum(abs(v) for v in shap_values.values())
    top_impact = sum(abs(v) for _, v in top)
    if total_impact > 0:
        coverage = top_impact / total_impact * 100
        lines.append(f"These {len(top)} features explain {coverage:.0f}% of the prediction.")

    return "\n".join(lines)


def get_top_contributors(
    shap_values: dict[str, float],
    n: int = 5,
) -> list[tuple[str, float]]:
    """Return the top-N features by absolute SHAP impact.

    Returns
    -------
    List of (feature_name, shap_value) sorted by descending |value|.
    """
    sorted_items = sorted(shap_values.items(), key=lambda kv: abs(kv[1]), reverse=True)
    return sorted_items[:n]


# ── Private helpers ──────────────────────────────────────────────────────────

def _fallback_importance(model: Any, feature_names: list[str]) -> dict[str, float]:
    """Extract feature importance from model coefficients when SHAP is unavailable."""
    coefs: np.ndarray | None = None
    if hasattr(model, "coef_"):
        coefs = np.abs(np.asarray(model.coef_).flatten())
    elif hasattr(model, "feature_importances_"):
        coefs = np.asarray(model.feature_importances_)

    if coefs is not None and len(coefs) == len(feature_names):
        return {name: round(float(c), 6) for name, c in zip(feature_names, coefs)}

    return {name: 0.0 for name in feature_names}


def _humanise_feature(name: str) -> str:
    """Convert snake_case feature names to human-readable labels."""
    return name.replace("_", " ").replace("pct", "%").title()
