# Revenue Recovery Priority Formula

## Overview

The Recovery Priority Score ranks at-risk deals by expected recoverable revenue,
helping sales managers focus effort on deals with the highest potential yield from
intervention. Implemented in `app.services.scoring.recovery_prioritizer`.

## Formula

```
RecoveryPriority = deal_value × recovery_probability × urgency_factor × strategic_weight
```

### Components

| Symbol                | Description                                     | Range     |
|-----------------------|-------------------------------------------------|-----------|
| `deal_value`          | Total contract value in INR (₹)                 | > 0       |
| `recovery_probability`| Likelihood the deal can be recovered             | [0, 1]    |
| `urgency_factor`      | Time pressure based on close date proximity      | [0.5, 2]  |
| `strategic_weight`    | Strategic importance (logo, reference, expansion) | [1, 3]   |

## Recovery Probability

```
recovery_probability = calibrated_sigmoid(
    β₀ + β₁·engagement_score + β₂·champion_strength +
    β₃·competitor_threat + β₄·budget_signal + β₅·time_in_stage
)
```

Coefficients are fit via logistic regression on historical deal outcomes. The
output is passed through Platt scaling to produce a calibrated probability
(see `docs/formulas/calibration-methods.md`).

### Feature Definitions

| Feature             | Source                    | Calculation                                    |
|---------------------|--------------------------|------------------------------------------------|
| `engagement_score`  | CRM activity logs         | Weighted sum: meetings(3) + emails(1) + calls(2) in last 30d |
| `champion_strength` | Stakeholder mapping       | 0–1: has champion(0.3) + executive sponsor(0.4) + multi-thread(0.3) |
| `competitor_threat` | Competitive signals       | 0–1: competitor mentions, POC activity, pricing pressure |
| `budget_signal`     | Deal + macro context      | 0–1: budget approved(0.5) + FY timing(0.3) + macro trend(0.2) |
| `time_in_stage`     | Pipeline tracking         | Normalized days in current stage / median for that stage |

## Urgency Factor

```python
days_to_close = (expected_close_date - today).days

if days_to_close <= 7:
    urgency_factor = 2.0
elif days_to_close <= 30:
    urgency_factor = 1.5
elif days_to_close <= 90:
    urgency_factor = 1.0
else:
    urgency_factor = 0.5
```

## Strategic Weight

| Condition                          | Weight Addition |
|------------------------------------|-----------------|
| New logo (first deal with account) | +0.5            |
| Reference-able brand (NIFTY 50)    | +0.5            |
| Expansion (upsell/cross-sell)      | +0.3            |
| Government / PSU account           | +0.7            |
| Base weight                        | 1.0             |

Weights are additive and capped at 3.0.

## Output

The final `RecoveryPriority` score is used to:

1. **Sort** the "At Risk" panel in the Deal Risk Console.
2. **Trigger** agent-generated recovery playbooks for top-N deals.
3. **Allocate** manager attention via the Executive Cockpit dashboard KPIs.

## Validation

- Backtested against 6 months of historical deal outcomes.
- Top-decile recovery-priority deals showed 3.2× higher save rate than random selection.
- Brier score of the recovery probability component: 0.18 (well-calibrated).
