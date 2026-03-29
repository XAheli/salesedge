# Deal Risk Console

## Overview

The Deals page (`/deals`) provides a pipeline view of all active deals, grouped by
risk level. It surfaces at-risk deals early so managers can intervene before revenue
is lost.

## Page Layout

### Risk Segments

Deals are grouped into four swim lanes:

| Segment     | Criteria                  | Color  | Action                      |
|-------------|---------------------------|--------|-----------------------------|
| **At Risk** | Risk score > 70           | Red    | Immediate intervention      |
| **Healthy** | Risk score 30–70          | Amber  | Monitor weekly              |
| **Won**     | Closed-won                | Green  | Celebrate + reference ask   |
| **Lost**    | Closed-lost               | Gray   | Post-mortem analysis        |

### Deal Cards

Each deal card displays:

- **Deal name** and associated company
- **Value** in ₹ lakhs/crore
- **Risk score** (0–100, higher = riskier)
- **Stage** — Discovery, Proposal, Negotiation, Closing
- **Days in stage** — highlighted red if above median for that stage
- **Key risk factors** — top 3 risk drivers as tags

### Deal Detail Panel

Click a card to see:

1. **Risk waterfall** — SHAP waterfall showing which factors contribute to the risk
   score (engagement drop, competitor activity, budget freeze, champion left).
2. **Timeline** — Chronological view of deal events, stage transitions, and signals.
3. **Recovery playbook** — AI-generated action plan ranked by recovery priority.
4. **Stakeholder map** — Key contacts with engagement recency and role.

## Understanding the Risk Score

The Deal Risk Score (0–100) predicts the probability a deal will be lost or stall.
Higher scores mean greater risk.

| Factor                | Weight | Signal                                |
|-----------------------|--------|---------------------------------------|
| Engagement velocity   | 25%    | Meeting/email frequency vs. baseline  |
| Stage duration        | 20%    | Days in stage vs. historical median   |
| Champion stability    | 15%    | Has champion left? Multi-threaded?    |
| Competitor presence   | 15%    | Competitive mentions in signals       |
| Budget signals        | 15%    | Budget approved? FY timing?           |
| Macro headwinds       | 10%    | Sector downturn, policy changes       |

## Workflows

### Daily Risk Review (Sales Manager)

1. Open `/deals` and focus on the **At Risk** lane.
2. Deals are sorted by **Recovery Priority** (highest recoverable value first).
3. For each at-risk deal, open the detail panel and review the recovery playbook.
4. Assign actions to reps: schedule executive meeting, send case study, offer pilot.

### Deal Post-Mortem

1. Filter the **Lost** lane by date range.
2. Click a lost deal to view the risk timeline — identify where intervention was missed.
3. Common loss patterns surface as tags (price, competitor, timing, champion loss).

## Tips

- Deals with a risk score increase of 15+ points in a week trigger a WebSocket
  alert — watch for the notification bell.
- Use the Deal Intel Agent at `/agents` for conversational deal analysis:
  "What are the risks for the Infosys deal?"
