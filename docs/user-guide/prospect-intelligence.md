# Prospect Intelligence

## Overview

The Prospects page (`/prospects`) is your primary tool for identifying and
prioritizing sales targets. It displays 40+ real Indian companies (NIFTY 50/100
constituents) enriched with government data, market signals, and AI-generated
fit scores.

## Page Layout

### Search & Filters

- **Search bar** — Type a company name, sector, or BSE/NSE symbol for instant filtering.
- **Sector filter** — Dropdown to narrow by industry (IT, Banking, Pharma, Energy, etc.).
- **Fit score range** — Slider to show only prospects above a minimum score threshold.
- **Sort** — Click column headers to sort by fit score, revenue, market cap, or sector.

### Prospect Table

| Column          | Description                                          |
|-----------------|------------------------------------------------------|
| Company         | Legal name + NSE/BSE symbol                          |
| Sector          | NIFTY sector classification                          |
| Market Cap      | Current market cap in ₹ crore                        |
| Revenue         | Latest annual revenue from MCA/BSE filings           |
| Fit Score       | AI-computed 0–100 score (higher = better fit)        |
| Signals         | Count of recent market/policy signals                |
| Status          | New / Contacted / Qualified / Disqualified           |

### Prospect Detail Drawer

Click any row to open the detail drawer showing:

1. **Company profile** — Industry, founding year, headquarters, key executives.
2. **Fit score breakdown** — SHAP-style waterfall chart explaining which factors
   increased or decreased the score (revenue scale, sector alignment, growth
   trajectory, government policy tailwinds).
3. **Market signals** — Recent news, RBI/SEBI policy changes, and price movements
   relevant to this company.
4. **Recommended actions** — AI-suggested outreach sequence with personalized hooks.

## Understanding the Fit Score

The Prospect Fit Score (0–100) quantifies how well a company matches SalesEdge's
ideal customer profile. It combines:

| Factor                | Weight | Source                          |
|-----------------------|--------|---------------------------------|
| Revenue scale         | 25%    | MCA annual filings              |
| Sector alignment      | 20%    | NIFTY sector classification     |
| Growth trajectory     | 20%    | Quarter-over-quarter revenue    |
| Digital maturity      | 15%    | Proxy signals (IT spend, hiring)|
| Policy tailwinds      | 10%    | Government policy signals       |
| Competitive whitespace| 10%    | Absence of incumbent vendors    |

Scores are calibrated so that a score of 70 means ~70% probability the prospect
will convert to a qualified opportunity within 90 days.

## Workflows

### Finding New Targets

1. Navigate to `/prospects`.
2. Sort by **Fit Score** descending.
3. Filter by your assigned sector.
4. Review the top 10 — open detail drawers to understand the scoring rationale.
5. Click "Generate Outreach" to create a personalized email sequence.

### Reviewing Signal-Rich Prospects

1. Sort by **Signals** column descending.
2. Prospects with 5+ recent signals likely have a trigger event (policy change,
   earnings surprise, leadership change) that creates an opening.
3. Open the detail drawer → Signals tab to read the specific triggers.

## Tips

- Refresh the page to pull the latest market data (cached for 5 minutes).
- Use the AI Agent chat (`/agents`) with "Analyze {company} as a prospect" for
  deeper, conversational analysis.
