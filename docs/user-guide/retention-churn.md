# Retention & Churn Analysis

## Overview

The Retention page (`/retention`) helps customer success teams identify accounts at
risk of churning and intervene with data-driven strategies. It combines usage
patterns, engagement signals, and macro context into a churn hazard score.

## Page Layout

### Summary Cards

| Card                 | Metric                                    |
|----------------------|-------------------------------------------|
| **Net Retention**    | Revenue-weighted retention rate (%)       |
| **At-Risk Accounts** | Count of accounts with churn score > 60   |
| **Churned (QTD)**    | Accounts lost this quarter                |
| **Saved (QTD)**      | At-risk accounts successfully retained    |

### Churn Risk Distribution

A histogram showing the distribution of churn scores across all active accounts.
The red zone (score > 60) is highlighted, and clicking a bar filters the table below.

### Risk Table

| Column            | Description                                  |
|-------------------|----------------------------------------------|
| Account           | Company name + contract value                |
| Churn Score       | 0–100 hazard score (higher = more likely)    |
| Trend             | ↑ ↓ → arrow showing score direction (30d)    |
| Top Risk Factor   | Primary churn driver                         |
| Last Engagement   | Days since last meaningful interaction       |
| Contract Renewal  | Date of next renewal                         |
| Recommended Action| AI-suggested intervention                    |

### Loss Reason Breakdown

A bar chart showing historical churn reasons: pricing, product gaps, competitor
switch, budget cuts, champion departure, poor support.

## Understanding the Churn Score

The Churn Hazard Score (0–100) estimates the probability an account will churn
within the next 90 days.

| Feature                   | Weight | Description                           |
|---------------------------|--------|---------------------------------------|
| Usage trend               | 25%    | Login frequency, feature adoption     |
| Engagement recency        | 20%    | Days since last meeting/email/call    |
| NPS / satisfaction proxy  | 15%    | Support ticket sentiment, survey data |
| Contract terms            | 15%    | Time to renewal, discount level       |
| Competitive signals       | 15%    | Competitor mentions, POC activity     |
| Macro / sector health     | 10%    | Sector downturn, budget freezes       |

The model uses a survival analysis (Cox proportional hazards) enhanced with
XGBoost for non-linear interactions. Output is calibrated via isotonic regression.

## Workflows

### Weekly Retention Review

1. Open `/retention` — review the summary cards.
2. Sort the risk table by **Churn Score** descending.
3. For accounts scoring > 70:
   - Check the **Top Risk Factor** — is it actionable?
   - Review the **Recommended Action** — assign to the CSM.
   - Click into the detail view for full risk explanation.

### Proactive Renewal Preparation

1. Filter by **Contract Renewal** within the next 60 days.
2. Cross-reference with churn score — high-risk renewals need executive attention.
3. Generate a renewal playbook via the Retention Agent: "Prepare a retention
   strategy for {account}."

## Alerts

- Accounts crossing the churn score threshold of 60 trigger a notification.
- Weekly email digest lists all newly at-risk accounts.
