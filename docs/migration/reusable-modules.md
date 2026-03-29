# Reusable Modules from WorldMonitor

## Adopted Modules

These modules were copied from the WorldMonitor reference repository and adapted
for SalesEdge's sales-focused domain.

### 1. Connector Framework (`app/connectors/`)

**Source:** `worldmonitor/connectors/base.py`

The abstract `BaseConnector` class provides:

- Standardized `fetch()` / `health_check()` interface
- Built-in retry with exponential backoff via `tenacity`
- Rate limiting per connector
- Structured error logging
- Cache integration hooks

**Adaptations for SalesEdge:**

- Added `REQUIRES_API_KEY` and `CACHE_TTL` class attributes
- Added `normalize()` method for Indian data formatting
- Extended error taxonomy (rate limit vs. auth vs. network)
- Added `quality_score()` hook for data quality assessment

### 2. Cache Manager (`app/cache/manager.py`)

**Source:** `worldmonitor/services/cache.py`

Three-tier caching architecture:

1. **L1:** In-memory LRU cache (per-process, ~100ms reads)
2. **L2:** Redis cache (shared across processes, ~5ms reads)
3. **L3:** Database fallback (last resort, ~50ms reads)

**Adaptations:**

- Added cache key namespacing by data source
- Added cache invalidation on ingestion events
- Added TTL configuration per data source category

### 3. Middleware Stack (`app/api/middleware/`)

**Source:** `worldmonitor/middleware/`

| Middleware       | Purpose                               |
|------------------|---------------------------------------|
| `request_id`    | Adds X-Request-ID header for tracing  |
| `rate_limiter`  | Per-IP rate limiting with Redis       |

**Adaptations:** Minimal — these are domain-agnostic.

### 4. Utility Functions (`app/utils/`)

**Source:** `worldmonitor/utils/`

| Utility            | Purpose                                   |
|--------------------|-------------------------------------------|
| `indian_formats`   | ₹ currency formatting, lakh/crore notation |
| `confidence`       | Confidence interval calculations           |
| `logging`          | Structured logging with structlog          |

### 5. Infrastructure Templates

| File                    | Purpose                          |
|-------------------------|----------------------------------|
| `docker-compose.yml`   | Multi-service dev stack          |
| `Dockerfile` (backend) | Multi-stage Python build         |
| `Dockerfile` (frontend)| Multi-stage Node + nginx build   |
| `alembic/`             | Database migration framework     |

## Modules NOT Adopted

See `removal-list.md` for the complete list of modules that were deliberately
excluded due to domain irrelevance (conflict/war/crisis modules).

## Integration Notes

All adopted modules were:

1. Reviewed for security vulnerabilities
2. Updated to Python 3.12 syntax (match statements, type hints)
3. Re-linted with `ruff` under SalesEdge's configuration
4. Covered with unit tests in `backend/tests/`
