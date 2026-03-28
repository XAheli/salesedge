# Government API Integrations (India)

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Catalog](catalog.md)

---

## data.gov.in (Open Government Data — OGD)

**Connector:** `app/connectors/government/ogd_india.py`  
**Base URL:** `https://api.data.gov.in`

### API usage

- Register on the National Data Sharing and Accessibility Policy (NDSAP) / OGD portal and obtain an API key.
- Pass the key as the `api-key` query parameter on each request (handled by `_apply_auth` in the connector).
- Prefer dataset `resource_id` calls for stable schemas; use search/catalog endpoints for discovery.

### Rate limits

- Limits are **key- and plan-specific**. Treat published quotas as authoritative; SalesEdge caches catalog and resource responses (`CACHE_TTL_CATALOG`, `CACHE_TTL_RESOURCE`) to minimize repeated calls.

### Key datasets

- Ministry-wise economic indicators, agricultural statistics, energy, and MOSPI-published resources mirrored on OGD.
- Use ministry filters (e.g. `MOSPI`, `RBI`) with `discover_datasets_by_ministry` patterns in code/tests.

### Auto-discovery

- `app/ingestion/discovery/ogd_crawler.py` and connector helpers walk catalog pages until exhaustion, respecting pagination.
- Feature flag: `enable_ogd_auto_discovery` (`app/config.py`).

---

## RBI DBIE

**Connector:** `app/connectors/government/rbi_dbie.py`

### Access pattern

- DBIE often exposes **HTML tables and downloadable series** rather than a single JSON API. The connector uses `_request_raw` paths from `BaseConnector` to fetch CSV/HTML and normalizes in the ingestion layer.

### Scraping approach

- Identify stable series IDs and download URLs; **cache aggressively** and **respect RBI robots/terms**.
- Parse with `beautifulsoup4` / `lxml` where HTML is unavoidable; prefer machine-readable downloads when listed.

### Key series (examples)

- Policy rates, money supply, FX reserves, sectoral credit — used as **macro_headwind** and context features for prospects and retention models.

### Normalization

- Map frequencies (daily/weekly/monthly) to a canonical timestamp; store **observation date in UTC**, display **IST** in UI via `formatIST` / backend equivalents.

---

## MOSPI

**Connector:** `app/connectors/government/mospi.py`

### Indicators

- National accounts (GDP components), CPI / inflation proxies, IIP-style production indices where exposed through OGD or MOSPI-linked resources.

### Update frequencies

- Typically **monthly or quarterly** releases. Align ingestion with **Tier 1** scheduler (daily batch is sufficient; publish-day backfill may be triggered manually).

### Integration tips

- Tie releases to **Indian financial year** where datasets use Apr–Mar conventions; document mapping in normalization metadata.

---

## MCA (Ministry of Corporate Affairs)

**Connector:** `app/connectors/government/mca.py`

### Access patterns

- Portal flows may require **session-based access** or file downloads for bulk data. Implement **throttling** and **audit logging** for any authenticated scraping.

### Use in SalesEdge

- Company identification, registration age, listing/charge flags feed **prospect firmographics** and **risk_detection** when combined with financial connectors.

---

## SEBI

**Connector:** `app/connectors/government/sebi.py`

### Regulatory data

- Circulars, mutual fund statistics, and issuer disclosures as exposed on public endpoints.

### Usage

- **competitive_intel** and **macro_context** for listed entities; ensure citations in user-facing text for compliance narratives.

---

## Operational checklist

| Check | Action |
|-------|--------|
| Terms | Review current OGD / RBI / MOSPI / MCA / SEBI terms before production crawl volume |
| Attribution | Retain publisher and dataset identifiers in provenance (`app/api/v1/data_provenance.py`) |
| Rate control | Combine scheduler tiering + Redis cache + circuit breaker |
| PII | Government open data should be non-PII; still avoid merging with personal data without basis |

---

[← Documentation index](../README.md)
