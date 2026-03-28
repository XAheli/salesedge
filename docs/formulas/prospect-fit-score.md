# Prospect Fit Score — Detailed Methodology

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Handbook](handbook.md) · [Documentation index](../README.md)

---

## Objective

Quantify how closely a company matches the go-to-market ICP so SDRs and AEs prioritize outreach and marketing can score inbound leads consistently.

## Feature blocks

| Feature key | Meaning | Normalisation highlights |
|-------------|---------|------------------------|
| `company_size_fit` | Revenue vs target bands (₹1–5 Cr, ₹5–50 Cr, ₹50–500 Cr) | 1 inside band; tapered outside |
| `industry_fit` | NIC division vs `TARGET_INDUSTRIES_NIC` | 1 / 0.4 / 0 |
| `technology_fit` | Stack overlap with target keywords | Count / cap |
| `growth_signal` | Revenue growth, hiring, funding | Min–max normalize |
| `engagement_signal` | Web visits, content downloads | Min–max normalize |
| `geographic_fit` | State in priority set | 1 or 0.2 |
| `regulatory_tailwind` | External favourability score | Direct \([0,1]\) or neutral 0.5 |
| `financial_health` | Margin, leverage | Min–max + inverted D/E |
| `indian_registration` | MCA, GST cadence, DPIIT, listing | Piecewise sum capped at 1 |

## Weighting

Default weights sum to 1.0; if not, the implementation renormalizes. Weights should be tuned per product line and reviewed quarterly.

## Confidence

`confidence` reflects **data completeness**, not epistemic uncertainty of the model. Missing CRM fields materially lower confidence even if the score looks high.

## Governance

- Document weight changes in change requests.  
- Prefer explainability strings surfaced to reps (top positive contributors).  
- For regulated industries, avoid discriminatory proxies; NIC/industry must be justified as business-relevant.

---

[← Handbook](handbook.md)
