"""Model calibration utilities.

Provides Platt scaling, calibration curves, Brier scores, and calibration
loss computation for probability models used throughout the scoring engines.
"""

from __future__ import annotations

from typing import Any

import numpy as np

try:
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.metrics import brier_score_loss

    _SKLEARN_AVAILABLE = True
except ImportError:  # pragma: no cover
    _SKLEARN_AVAILABLE = False


def platt_scaling(
    model: Any,
    X_val: np.ndarray,
    y_val: np.ndarray,
    method: str = "sigmoid",
    cv: int | str = "prefit",
) -> Any:
    """Apply Platt scaling (sigmoid calibration) to a fitted classifier.

    Parameters
    ----------
    model : fitted estimator
        Must support ``predict_proba`` or ``decision_function``.
    X_val : array of shape (n_samples, n_features)
        Held-out validation features.
    y_val : array of shape (n_samples,)
        True binary labels.
    method : "sigmoid" (Platt) or "isotonic"
    cv : "prefit" to calibrate the supplied model as-is.

    Returns
    -------
    Calibrated classifier wrapping the original model.
    """
    if not _SKLEARN_AVAILABLE:
        raise RuntimeError("scikit-learn is required for Platt scaling")

    calibrated = CalibratedClassifierCV(model, method=method, cv=cv)
    calibrated.fit(X_val, y_val)
    return calibrated


def compute_calibration_curve(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bins: int = 10,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute a reliability diagram (calibration curve).

    Parameters
    ----------
    y_true : binary ground truth
    y_pred : predicted probabilities
    n_bins : number of equally-spaced bins

    Returns
    -------
    (mean_predicted, fraction_positive) arrays of length <= n_bins.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    mean_predicted: list[float] = []
    fraction_positive: list[float] = []

    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (y_pred >= lo) & (y_pred < hi)
        if not mask.any():
            continue
        mean_predicted.append(float(y_pred[mask].mean()))
        fraction_positive.append(float(y_true[mask].mean()))

    return np.array(mean_predicted), np.array(fraction_positive)


def compute_brier_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Compute the Brier score (mean squared error of probabilities).

    Lower is better; 0 = perfect calibration, 0.25 = maximum uncertainty.
    """
    if _SKLEARN_AVAILABLE:
        return float(brier_score_loss(y_true, y_pred))

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean((y_true - y_pred) ** 2))


def compute_calibration_loss(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bins: int = 10,
) -> float:
    """Compute expected calibration error (ECE).

    ECE is the weighted average of per-bin |accuracy - confidence|.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    n = len(y_true)
    if n == 0:
        return 0.0

    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0

    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (y_pred >= lo) & (y_pred < hi)
        bin_count = mask.sum()
        if bin_count == 0:
            continue
        bin_acc = y_true[mask].mean()
        bin_conf = y_pred[mask].mean()
        ece += (bin_count / n) * abs(bin_acc - bin_conf)

    return float(ece)
