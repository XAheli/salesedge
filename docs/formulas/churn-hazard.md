# Churn Hazard — Detailed Methodology

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Handbook](handbook.md) · [Documentation index](../README.md)

---

## Objective

Estimate \(P(\text{churn in next 90 days} \mid X)\) for Customer Success and Account Management, prioritizing saves and expansion defenses.

## Feature vector (`FEATURE_NAMES`)

| Feature | Direction (risk ↑ when…) |
|---------|---------------------------|
| `usage_trend_30d` | Negative trend increases churn risk |
| `support_ticket_frequency` | More tickets → risk |
| `nps_score` | Lower NPS → risk |
| `payment_delays` | More delays → risk |
| `champion_turnover` | Champion left → risk |
| `competitive_mentions` | More mentions → risk |
| `contract_renewal_proximity` | Closer renewal + stress → risk |
| `macro_headwind` | Higher macro stress → risk |

## Model modes

1. **Heuristic logistic:** Default \(\beta\) and intercept; always available.  
2. **Trained sklearn:** `LogisticRegression` + `CalibratedClassifierCV` for calibrated probabilities.

## Risk bands

| Level | Probability range |
|-------|-------------------|
| low | \([0, 0.25)\) |
| medium | \([0.25, 0.50)\) |
| high | \([0.50, 0.75)\) |
| critical | \([0.75, 1.0]\) |

## Interventions

Downstream `retention_agent` maps probability bands to playbooks (QBR, executive sponsor, training, commercial).

## Training hygiene

- Use **class weights** for imbalance.  
- Freeze feature definitions and document scaling.  
- Evaluate with **Brier score** and **calibration plots**.

---

[← Handbook](handbook.md)
