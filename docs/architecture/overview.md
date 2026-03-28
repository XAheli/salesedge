# System Architecture Overview

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md)

---

## System context (ASCII)

```
                    ┌─────────────────────────────────────────────────────────┐
                    │                    USERS                                 │
                    │   Sales reps │ RevOps │ Leadership │ Compliance viewers   │
                    └───────────────────────────┬─────────────────────────────┘
                                                │ HTTPS
                                                ▼
┌──────────────────────┐              ┌─────────────────────────────────────────┐
│  External data APIs  │              │           SalesEdge PLATFORM             │
│  Govt / Markets /    │◄────async────│  React SPA ◄──► FastAPI backend         │
│  Enrichment / CRM    │    connectors│       │              │                  │
└──────────────────────┘              │       │         Agents + scoring        │
                                        │       │              │                  │
                                        │       └──────► Feature store / cache    │
                                        └─────────────────────────────────────────┘
                                                │
                    ┌───────────────────────────┼───────────────────────────┐
                    ▼                           ▼                           ▼
              PostgreSQL                     Redis                    DuckDB *
            (transactional,                  (L2 cache,                (analytics /
             CRM mirror,                     sessions)                 columnar *)
             provenance)

* DuckDB is a first-class dependency for analytical workloads; deployment as a
  dedicated “L3” service may be in-process or sidecar depending on environment.
```

## Container diagram

| Container | Responsibility | Primary tech |
|-----------|----------------|--------------|
| **Frontend** | SPA, executive cockpit, data visualization, auth UX | React 18, Vite, TypeScript, Tailwind |
| **Backend API** | REST/OpenAPI, connectors, ingestion, agents, scoring | FastAPI, Pydantic, SQLModel, httpx |
| **PostgreSQL** | Persistent entities, audit, provenance metadata | PostgreSQL 16 |
| **Redis** | Distributed cache, rate-limit backing store | Redis 7 |
| **DuckDB** | Columnar analytics, large joins on ingested datasets | DuckDB (Python client) |
| **Reverse proxy (prod)** | TLS termination, static assets | nginx (see `docker-compose.prod.yml`) |

Local development often runs **Postgres + Redis** via Docker Compose and the API/UI on the host (`make dev-backend` / `make dev-frontend`).

## Technology stack

| Layer | Choices | Rationale |
|-------|---------|-----------|
| API | FastAPI + Uvicorn | Native async/await for concurrent connector I/O |
| Validation | Pydantic v2 | Runtime + OpenAPI schema alignment |
| ORM / migrations | SQLModel + Alembic | Typed models shared with API schemas |
| HTTP client | httpx | Async client with timeout and HTTP/1.1 stability |
| Resilience | tenacity, circuit breaker (custom) | Retries for transport errors; fail-fast when upstreams are unhealthy |
| Cache | In-memory LRU + Redis | Low-latency hot paths without stampeding origins |
| ML | scikit-learn, optional XGBoost | Calibrated churn models; explainability hooks |
| Observability | structlog, prometheus-client | Structured logs; metrics-ready instrumentation |
| Frontend | React, TanStack Query, Zustand | SPA with server-state caching |
| Testing | pytest, Vitest, Playwright, Locust | Backend/frontend/unit/E2E/performance |

## Key architectural decisions

1. **FastAPI for async I/O** — Connectors fan out to dozens of third-party APIs; async endpoints and `httpx` avoid thread-pool exhaustion.
2. **React SPA** — Rich dashboards (Nivo/Recharts) and executive views without full page reloads; API contract via OpenAPI.
3. **Multi-tier caching** — L1 process memory (`CacheManager`) → L2 Redis → origin fetch reduces cost and respects rate limits.
4. **Circuit breaker pattern** — Implemented on `BaseConnector` to stop calling failing upstreams and allow recovery via half-open probes.
5. **Agent modularization** — Prospect, Deal Intel, Retention, and Competitive agents share `BaseAgent` and are coordinated by `AgentOrchestrator`.
6. **Indian context first** — INR formatting, IST timestamps, NIC/MCA/GST-aware prospect features in scoring.

## Data flow overview

1. **Ingress** — Scheduled jobs (`IngestionScheduler`) and on-demand API calls invoke connector modules under `app/connectors/`.
2. **Pipeline** — Raw payloads pass through normalization, deduplication, and quality scoring (`app/ingestion/`).
3. **Storage** — Canonical records and lineage land in PostgreSQL; hot slices are cached in Redis; analytical exports can be queried via DuckDB-oriented paths.
4. **Features** — `app/feature_store/` assembles prospect, deal, and macro features for models and agents.
5. **Consumption** — REST handlers under `app/api/v1/` serve the UI; agents emit signals and recommended actions.

See [Data flow](data-flow.md) and [Agent architecture](agent-architecture.md) for detail.

---

[← Documentation index](../README.md)
