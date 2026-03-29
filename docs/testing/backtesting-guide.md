# Backtesting Guide

## Purpose

Backtesting validates SalesEdge's scoring models against historical data to ensure
predictions (deal risk, churn probability, prospect fit) would have been accurate
in the past before deploying them for live decisions.

## Historical Replay Methodology

### Data Requirements

| Dataset             | Source                  | Minimum History |
|---------------------|-------------------------|-----------------|
| Deal outcomes       | CRM / seeded data       | 6 months        |
| Prospect conversions| Pipeline tracking        | 6 months        |
| Churn events        | Account health records   | 12 months       |
| Market signals      | Connector snapshots      | 3 months        |

### Replay Architecture

```
historical_data/
├── deals_2024H1.parquet      # Deals with known outcomes
├── prospects_2024H1.parquet  # Prospects with conversion labels
├── signals_2024H1.parquet    # Market signals timestamped
└── accounts_2024.parquet     # Account health with churn labels
```

1. **Snapshot loading:** Load historical state at time `t₀`.
2. **Feature computation:** Run the feature store pipeline as-of `t₀` (no future leakage).
3. **Model scoring:** Score each entity using the model under test.
4. **Outcome comparison:** Compare predictions to actual outcomes at `t₀ + horizon`.
5. **Metric computation:** Calculate precision, recall, AUC, Brier score, calibration curve.

### Time-Based Cross-Validation

```
│── Train ──│── Cal ──│── Test ──│
     t₀         t₁        t₂

Fold 1: Jan-Mar train  │ Apr cal  │ May test
Fold 2: Feb-Apr train  │ May cal  │ Jun test
Fold 3: Mar-May train  │ Jun cal  │ Jul test
```

Each fold uses a 3-month training window, 1-month calibration, 1-month test. This
expanding-window approach prevents temporal leakage.

## Running Backtests

```bash
# Full backtest suite
./scripts/run-backtests.sh

# Specific model
./scripts/run-backtests.sh --model deal_risk

# Custom date range
./scripts/run-backtests.sh --start 2024-01-01 --end 2024-06-30
```

## Metrics & Thresholds

| Metric              | Target     | Action if Below                    |
|---------------------|------------|------------------------------------|
| AUC-ROC             | ≥ 0.75     | Retrain with expanded features     |
| Precision @top-10%  | ≥ 0.60     | Adjust decision threshold          |
| Brier score         | ≤ 0.25     | Recalibrate (Platt or isotonic)    |
| Calibration slope   | 0.8–1.2    | Indicates systematic bias          |

## Artifacts

Each backtest run produces:

- `results/{model}_{date}/metrics.json` — Scalar metrics
- `results/{model}_{date}/calibration_curve.png` — Reliability diagram
- `results/{model}_{date}/roc_curve.png` — ROC curve
- `results/{model}_{date}/predictions.parquet` — Full prediction log

## Anti-Leakage Checklist

- [ ] Features computed only from data available at prediction time
- [ ] No shuffling across time boundaries
- [ ] Calibration set is disjoint from train and test
- [ ] Market signals filtered by `fetched_at < prediction_time`
