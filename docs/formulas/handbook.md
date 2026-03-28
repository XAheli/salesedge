# Formula Handbook (Sections 9.1–9.4)

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md)

Implementation references: `app/services/scoring/prospect_scorer.py`, `deal_risk_scorer.py`, `churn_predictor.py`, `recovery_prioritizer.py`.

---

## 9.1 Prospect Fit Score

**Purpose:** Rank leads and accounts by alignment to the Ideal Customer Profile (ICP), including India-specific registration and geography signals.

**Variables**

| Symbol | Description | Typical source |
|--------|-------------|----------------|
| \(f_i(p)\) | Raw feature value for prospect \(p\) | Connectors + CRM |
| \(\tilde{f}_i\) | Feature after normalization to \([0,1]\) | Scorer |
| \(w_i\) | Non-negative weight; \(\sum_i w_i = 1\) | Config / `DEFAULT_WEIGHTS` |

**Mathematical formula**

\[
\text{FitScore}(p) = 100 \cdot \sum_i w_i \cdot \tilde{f}_i(p)
\]

(clamped to \([0, 100]\) after scaling in code).

**Normalization:** Per-feature min–max or rule-based maps (e.g. NIC division membership → \(\{0, 0.4, 1\}\)).

**Default weights (implementation):** `company_size_fit`, `industry_fit`, `technology_fit`, `growth_signal`, `engagement_signal`, `geographic_fit`, `regulatory_tailwind`, `financial_health`, `indian_registration` — see `DEFAULT_WEIGHTS` in code.

**Uncertainty estimation:** `confidence` = fraction of features with non-null data (floor 0.1).

**Calibration:** Platt / isotonic calibration can be layered on top of the linear score if labelled win/loss data exists (`app/services/scoring/calibration.py`).

**Backtest requirements:** Hold-out by time and industry; report precision@k for “converted” definition; calibration curve (Brier score).

**Indian context adjustments:** NIC codes, state codes (`TARGET_STATES`), GST filing cadence, DPIIT recognition, MCA registration date, listed exchange.

**Worked example:** Revenue ₹12 Cr, NIC `62*`, state `KA`, monthly GST, DPIIT true → high `company_size_fit`, `industry_fit`, `indian_registration`; score dominated by those terms.

**Detail:** [prospect-fit-score.md](prospect-fit-score.md)

---

## 9.2 Deal Risk Score

**Purpose:** Estimate likelihood of deal slippage or loss from engagement, stakeholder, sentiment, and value-drift signals.

**Variables**

| Symbol | Description |
|--------|-------------|
| \(\text{health}_j(d)\) | Health of component \(j\), in \([0,1]\) (1 = healthy) |
| \(w_j\) | Weights summing to 1 |

**Mathematical formula**

\[
\text{RiskScore}(d) = 100 \cdot \bigl(1 - \sum_j w_j \cdot \text{health}_j(d)\bigr)
\]

**Normalization:** Each health sub-score is already in \([0,1]\) via ratios, caps, or logistic-style mappings.

**Default weights:** `engagement_momentum`, `stakeholder_coverage`, `stage_velocity`, `sentiment_trend`, `competitor_presence`, `contract_value_drift`, `stakeholder_entropy`.

**Uncertainty estimation:** Confidence from presence of events, stakeholders, sentiment, initial value, and stage metadata.

**Calibration:** Map risk deciles to historical loss rates per stage.

**Backtest requirements:** Label deals as won/lost/stalled; measure AUC and calibration at 30/60/90-day horizons.

**Indian context adjustments:** Deal values in INR; expected stage SLAs may differ for enterprise public-sector cycles (configure `expected_stage_days`).

**Worked example:** Low events vs baseline, single-threaded, sentiment average negative → low health → risk in upper deciles.

**Detail:** [deal-risk-score.md](deal-risk-score.md)

---

## 9.3 Churn Hazard Estimate

**Purpose:** Estimate probability of churn in the next 90 days for existing customers.

**Variables**

| Symbol | Description |
|--------|-------------|
| \(X\) | Feature vector (usage trend, tickets, NPS, delays, …) |
| \(\beta\) | Learned or default coefficients |
| \(b\) | Intercept |

**Mathematical formula**

\[
P(\text{churn} \mid X) = \sigma(\beta \cdot X + b) = \frac{1}{1 + e^{-(\beta \cdot X + b)}}
\]

With trained sklearn pipeline: **Platt scaling** via `CalibratedClassifierCV` when `fit()` is used.

**Normalization:** Features should be scaled consistently between training and inference (document transforms per deployment).

**Default coefficients:** See `DEFAULT_COEFFICIENTS` and `DEFAULT_INTERCEPT` when no model is trained.

**Uncertainty estimation:** Wald-style interval on probability in `ChurnPredictor._compute_ci`.

**Calibration:** Reliability diagrams; recalibrate quarterly when base rates shift.

**Backtest requirements:** Time-based CV; precision/recall at policy thresholds; segment by ARR band.

**Indian context adjustments:** Payment delay semantics (NEFT/RTGS holidays), GST billing cycles, macro_headwind from RBI/MOSPI features.

**Worked example:** Rising tickets + payment delays + champion turnover → probability crosses `high` band (0.5–0.75).

**Detail:** [churn-hazard.md](churn-hazard.md)

---

## 9.4 Revenue Recovery Priority

**Purpose:** Rank at-risk deals for sales leadership so effort focuses on **high risk × high value × recoverable** opportunities.

**Variables**

| Symbol | Description |
|--------|-------------|
| \(R(d)\) | Deal risk score (0–100) |
| \(V(d)\) | Contract value (INR) |
| \(\rho(d)\) | Recoverability estimate in \([0,1]\) |

**Mathematical formula (implementation)**

\[
\text{RecoveryPriority}(d) = 100 \cdot \frac{R(d)}{100} \cdot \tilde{V}(d) \cdot \rho(d)
\]

where \(\tilde{V}(d) = \min\left(\frac{\log(1 + V(d))}{\log(1 + V_{\text{scale}})}, 1\right)\) with \(V_{\text{scale}} = 10^8\) INR (see `VALUE_SCALE_INR`).

**Normalization:** Log compresses mega-deals; recoverability blends stage priors and relationship signals.

**Weights:** Implicit in how \(\rho\) aggregates champion, multi-threading, engagement, competitors, executive sponsor.

**Uncertainty estimation:** Report top-\(k\) list with risk confidence from Section 9.2.

**Calibration:** Compare predicted recovery rate by priority decile after 30 days.

**Backtest requirements:** Historical win-backs vs priority rank; sensitivity to \(V_{\text{scale}}\).

**Indian context adjustments:** INR values; enterprise deals often need executive sponsor threshold tuned above ₹5 Cr (see `RecoveryPrioritizer`).

**Worked example:** Risk 80, ₹8 Cr, negotiation stage with champion → high \(\rho\) → priority rank near top.

---

[← Documentation index](../README.md)
