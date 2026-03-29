# Score Calibration Methods

## Purpose

Raw model outputs (logistic regression, XGBoost) produce scores that are often
poorly calibrated — a score of 0.7 doesn't reliably mean a 70% probability of the
positive event. SalesEdge applies post-hoc calibration to all customer-facing
probability scores. Implemented in `app.services.scoring.calibration`.

## Platt Scaling

The primary calibration method. Fits a logistic regression on top of the raw model
output using a held-out calibration set.

```
calibrated_p = 1 / (1 + exp(-(A · raw_score + B)))
```

Where `A` and `B` are learned from the calibration set by minimizing log-loss.

### Training Procedure

1. Split labeled data: 70% train / 15% calibration / 15% test.
2. Train the primary model (e.g., XGBoost for churn) on the train set.
3. Generate raw predictions on the calibration set.
4. Fit `sklearn.linear_model.LogisticRegression` with `raw_score` as the single
   feature and the true label as the target.
5. Store `A` (coefficient) and `B` (intercept) as the calibration parameters.

### When to Use

- Binary classification models (deal win/loss, churn yes/no).
- Models with monotonic outputs (higher score ≈ higher probability).

## Isotonic Regression (Fallback)

Non-parametric alternative when Platt scaling's sigmoid assumption is too rigid.

```python
from sklearn.isotonic import IsotonicRegression

ir = IsotonicRegression(out_of_bounds='clip')
ir.fit(raw_scores_cal, labels_cal)
calibrated_p = ir.predict(raw_scores_test)
```

### When to Use

- Ensemble models with non-sigmoid score distributions.
- When the calibration curve shows non-monotonic behavior after Platt scaling.
- Requires more calibration data (≥500 samples) to avoid overfitting.

## Calibration Curve (Reliability Diagram)

Visual diagnostic that bins predictions into quantiles and compares predicted
probability against observed frequency.

```
For each bin b in [0.0–0.1, 0.1–0.2, ..., 0.9–1.0]:
    predicted_mean = mean(scores in bin b)
    observed_freq  = count(positive in bin b) / count(all in bin b)
    Plot: (predicted_mean, observed_freq)
```

A perfectly calibrated model lies on the diagonal `y = x`. Deviations indicate:

- **Above diagonal:** Model is under-confident (scores too low).
- **Below diagonal:** Model is over-confident (scores too high).

SalesEdge generates calibration curves during backtesting (`scripts/run-backtests.sh`)
and stores them as artifacts for each model version.

## Brier Score

Scalar metric measuring calibration quality. Lower is better.

```
Brier = (1/N) × Σ (predicted_i - actual_i)²
```

| Range       | Interpretation          |
|-------------|-------------------------|
| 0.00–0.10   | Excellent calibration   |
| 0.10–0.20   | Good calibration        |
| 0.20–0.30   | Fair — consider recalibrating |
| > 0.30      | Poor — model needs retraining  |

### Brier Decomposition

```
Brier = Reliability - Resolution + Uncertainty
```

- **Reliability:** Measures calibration error (want low).
- **Resolution:** Measures discriminative ability (want high).
- **Uncertainty:** Measures inherent class balance (fixed for a dataset).

## Current Model Calibration Status

| Model              | Method          | Brier Score | Last Calibrated |
|--------------------|-----------------|-------------|-----------------|
| Prospect Fit       | Platt scaling   | 0.14        | On each seed    |
| Deal Risk          | Platt scaling   | 0.16        | On each seed    |
| Churn Hazard       | Isotonic        | 0.18        | On each seed    |
| Recovery Priority  | Platt scaling   | 0.18        | On each seed    |

## Recalibration Triggers

1. **Data drift:** Monthly check — if KL divergence of score distribution > 0.1.
2. **Performance drop:** If Brier score on last 30 days of predictions > 0.25.
3. **Model retrain:** Every calibration set is refreshed when the primary model is retrained.
