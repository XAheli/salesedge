# Deal Risk Score — Detailed Methodology

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Handbook](handbook.md) · [Documentation index](../README.md)

---

## Objective

Surface deals that are **statistically fragile** before they stall: low engagement, poor stakeholder coverage, negative sentiment, competitor pressure, or shrinking contract value.

## Health components

| Component | Interpretation |
|-----------|----------------|
| `engagement_momentum` | Recent activity rate vs `baseline_event_rate` |
| `stakeholder_coverage` | Share of known decision-makers engaged |
| `stage_velocity` | `days_in_stage` vs `expected_stage_days` |
| `sentiment_trend` | Mean comms sentiment mapped from \([-1,1]\) to health |
| `competitor_presence` | Decay with competitor mention count |
| `contract_value_drift` | Current / initial INR value (capped) |
| `stakeholder_entropy` | Evenness of engagement across stakeholders (Shannon) |

## Risk interpretation

- **Low risk (score near 0):** Weighted health near 1 — pipeline healthy.  
- **High risk (score near 100):** Multiple health components collapsed.

## Configuration

- Per-stage `expected_stage_days` should reflect **your** sales methodology.  
- `baseline_event_rate` should be re-estimated by segment (SMB vs enterprise).

## Explainability

The engine lists the **weakest** components first so managers can coach with specificity.

---

[← Handbook](handbook.md)
