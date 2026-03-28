# Data Ingestion and Processing Flow

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Architecture overview](overview.md)

---

## End-to-end pipeline

```
Connectors (BaseConnector subclasses)
        │
        ▼
┌───────────────────┐
│ Ingestion pipeline │  orchestration, batching, error handling
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Normalization      │  units, currencies → INR, timestamps → UTC/IST display
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Quality scoring    │  completeness, freshness, source trust
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Feature store      │  prospect / deal / macro feature vectors
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Models & agents    │  fit/risk/churn/recovery + orchestrated actions
└───────────────────┘
```

Implementation anchors: `app/ingestion/pipeline.py`, `normalization.py`, `quality_scorer.py`, `app/feature_store/`.

## Multi-tier caching

| Tier | Technology | Role | Typical TTL |
|------|------------|------|-------------|
| **L1** | In-memory LRU (`_L1Cache` in `CacheManager`) | Per-process deduplication of identical keys | Seconds–minutes (per key TTL) |
| **L2** | Redis | Shared cache across API workers; survives process restart | Minutes–hours (connector-defined) |
| **L3** | DuckDB | Analytical cache / Parquet-backed marts (workload-dependent) | Refresh on ETL schedule |
| **L4** | PostgreSQL | System of record, provenance, idempotent ingestion keys | Durable |

Connector HTTP paths use `cache_key` + `cache_ttl` on `_request()` to populate L1/L2 when a `CacheManager` is wired in.

## Bootstrap hydration pattern

On application or worker startup:

1. **Config** — Load `SE_*` settings (`app/config.py`) so required keys (e.g. `SE_OGD_API_KEY`) are available before connectors run.
2. **Infrastructure** — `scripts/bootstrap.sh` brings up Postgres/Redis, runs Alembic, optional seed.
3. **Registry** — `auto_discover_connectors()` imports connector modules so they can self-register with `ConnectorRegistry`.
4. **Warm paths** — Optional: prefetch high-value catalog metadata (e.g. OGD dataset index) into Redis to avoid cold UI loads.

This pattern avoids serving empty dashboards on first request after deploy.

## Scheduled ingestion frequencies by tier

Defined in `app/ingestion/scheduler.py` as `TIER_SCHEDULES`:

| Tier | Name | Default schedule | Notes |
|------|------|------------------|-------|
| **1** | Government | Daily cron, **06:00 IST** | MOSPI/RBI/SEBI-class datasets; low churn, high compliance value |
| **2** | Market | **Every 15 minutes** between **09:15–15:30 IST** | Aligns with NSE/BSE cash session |
| **3** | Enrichment | **Hourly** | Quotes, FX, crypto, third-party fundamentals |
| **4** | CRM / internal | On-demand or webhook-driven | Simulated or live CRM connectors; not in default tier table |

Custom schedules can be passed per connector via `schedule_connector(..., custom_schedule=...)`.

---

[← Documentation index](../README.md)
