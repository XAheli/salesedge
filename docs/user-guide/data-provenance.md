# Data Provenance

## Overview

The Data page (`/data`) provides transparency into where SalesEdge's data comes
from, how fresh it is, and whether each source is healthy. This is critical for
building trust in AI-generated scores and recommendations.

## Page Layout

### Connectivity Dashboard

A grid of source cards showing real-time status:

| Status     | Icon   | Meaning                                    |
|------------|--------|--------------------------------------------|
| Connected  | 🟢     | Last fetch succeeded, data is fresh        |
| Degraded   | 🟡     | Last fetch succeeded but data is stale     |
| Error      | 🔴     | Last fetch failed, using cached data       |
| Disabled   | ⚪     | Source not configured (API key missing)     |

### Source Detail Table

| Column          | Description                                       |
|-----------------|---------------------------------------------------|
| Source           | API name (e.g., "data.gov.in", "Finnhub")        |
| Category         | Government / Market / Enrichment / Broker         |
| Last Fetched     | Timestamp of most recent successful fetch         |
| Records          | Count of records from this source                 |
| Quality Score    | Completeness × freshness × accuracy (0–1)        |
| Latency          | Average API response time (ms)                    |
| Error Rate       | Failed requests / total requests (last 24h)       |

### Quality Score Breakdown

Click any source to see the quality score decomposition:

- **Completeness** (0–1) — Fraction of expected fields that are non-null.
- **Freshness** (0–1) — Decays exponentially based on time since last update.
  `freshness = exp(-λ × hours_since_update)` where λ varies by source.
- **Accuracy** (0–1) — Cross-validation against secondary sources when available.

### Data Lineage View

For any prospect or deal, trace exactly which data sources contributed to its
scores:

```
Reliance Industries (Prospect Fit: 82)
├── Company profile     → MCA filings (fetched 2h ago)
├── Market cap          → NSE quote (fetched 5m ago)
├── Revenue             → BSE annual report (fetched 12h ago)
├── Sector signals      → RBI DBIE (fetched 6h ago)
├── Competitor context  → Finnhub peers (fetched 15m ago)
└── Policy tailwinds    → data.gov.in (fetched 3h ago)
```

## Workflows

### Verifying Data Trust

Before sharing a score or recommendation with a customer, check the Data page to
confirm all contributing sources are connected and fresh.

### Troubleshooting a Stale Score

1. Open `/data` — find the degraded/error sources.
2. Check the **Error Rate** column for recent failures.
3. Click the source → view error logs (last 5 failures with status codes).
4. Common issues: expired API key, rate limit exceeded, upstream API down.
5. Fix: update the key in `.env` and restart, or wait for rate limit reset.

### Monitoring Data Quality Trends

The bottom section of the page shows a 7-day trend chart for:

- Aggregate quality score across all sources
- Ingestion volume (records/hour)
- API error rate

A declining quality trend triggers an automated alert to the platform admin.

## API Endpoints

| Endpoint                          | Method | Description                 |
|-----------------------------------|--------|-----------------------------|
| `/api/v1/data-provenance/sources` | GET    | All sources with status     |
| `/api/v1/data-provenance/health`  | GET    | Summary health check        |
