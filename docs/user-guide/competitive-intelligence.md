# Competitive Intelligence

## Overview

The Intelligence page (`/intelligence`) aggregates competitive signals from
government policy changes (RBI, SEBI), competitor funding rounds, market movements,
and news feeds. It powers battlecard generation and real-time competitive alerts.

## Page Layout

### Signal Feed

A chronological feed of intelligence signals with:

| Field        | Description                                          |
|--------------|------------------------------------------------------|
| Timestamp    | When the signal was detected                         |
| Source       | API source (RBI, SEBI, Finnhub, RSS, etc.)          |
| Category     | Policy, Funding, Pricing, Product, Leadership, M&A   |
| Relevance    | High / Medium / Low based on impact scoring          |
| Summary      | One-line description of the signal                   |
| Entities     | Companies, sectors, or products mentioned            |

### Policy Tracker

Dedicated section for government/regulatory signals:

- **RBI monetary policy** — Rate decisions, liquidity measures
- **SEBI regulations** — New listing rules, compliance changes
- **Union Budget** — Sector-specific allocations, tax changes
- **Industry policy** — PLI schemes, FDI policy updates

### Competitor Cards

For each tracked competitor:

1. **Activity summary** — Recent signals aggregated into a score.
2. **Funding events** — Latest rounds, valuations, investors.
3. **Product moves** — New launches, feature announcements.
4. **Win/loss trends** — Where you're winning or losing against them.

### Battlecard Generator

Click "Generate Battlecard" on any competitor to produce:

- **Strengths** — Where they outperform you
- **Weaknesses** — Gaps you can exploit
- **Talk tracks** — Objection handling scripts
- **Proof points** — Case studies and data points to counter their claims
- **Pricing intelligence** — Known pricing model and discount patterns

## Signal Scoring

Each signal receives a relevance score based on:

| Factor           | Weight | Description                              |
|------------------|--------|------------------------------------------|
| Entity overlap   | 30%    | Does it mention your accounts/prospects? |
| Sector relevance | 25%    | Is it in your target sectors?            |
| Recency          | 20%    | Hours since publication                  |
| Source authority  | 15%    | Government > wire service > blog         |
| Sentiment impact | 10%    | Positive/negative for your position      |

## Workflows

### Daily Intel Scan

1. Open `/intelligence` — scan the signal feed for High-relevance items.
2. Policy signals from RBI/SEBI often create urgency — use them as conversation
   starters with prospects in affected sectors.
3. Competitor funding signals indicate increased competitive pressure.

### Preparing for a Competitive Deal

1. Identify the competitor in the deal.
2. Navigate to their Competitor Card on the Intelligence page.
3. Click "Generate Battlecard" to get a fresh analysis.
4. Review talk tracks and share with the account executive.
5. For deeper analysis, use the Competitive Agent: "Generate a battlecard against
   {competitor} for the {account} deal."

## Data Sources

| Source Category    | Connectors                              | Refresh Rate |
|--------------------|-----------------------------------------|-------------|
| Government policy  | OGD, RBI DBIE, SEBI, MOSPI             | 6 hours      |
| Market data        | NSE, BSE, broker APIs                  | 5 minutes    |
| Company intel      | Finnhub, FMP, Alpha Vantage            | 15 minutes   |
| News               | RSS business feeds                     | 30 minutes   |
