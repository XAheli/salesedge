# Repository Audit — WorldMonitor Reference

## Purpose

This document audits the WorldMonitor reference repository to identify reusable
modules, patterns, and code that can accelerate SalesEdge development while
ensuring all war/conflict-related functionality is removed.

## Repository Overview

| Attribute     | WorldMonitor                                |
|---------------|---------------------------------------------|
| Purpose       | Global events monitoring & analysis platform |
| Stack         | Python 3.11, FastAPI, React, PostgreSQL     |
| Data sources  | Government APIs, news feeds, market data    |
| AI/ML         | scikit-learn, LLM integrations              |

## Module Inventory

### Reusable Modules (adopted in SalesEdge)

| Module                    | WM Path                      | SE Path                          | Status    |
|---------------------------|------------------------------|----------------------------------|-----------|
| Connector base class      | `connectors/base.py`         | `app/connectors/base.py`        | Adopted   |
| OGD India connector       | `connectors/govt/ogd.py`     | `app/connectors/government/ogd_india.py` | Adapted |
| Cache manager             | `services/cache.py`          | `app/cache/manager.py`          | Adapted   |
| Rate limiter middleware    | `middleware/rate_limit.py`   | `app/api/middleware/rate_limiter.py` | Adopted |
| Request ID middleware      | `middleware/request_id.py`   | `app/api/middleware/request_id.py` | Adopted |
| Indian number formatting   | `utils/formats.py`           | `app/utils/indian_formats.py`   | Adopted   |
| Structured logging setup   | `utils/logging.py`           | `app/utils/logging.py`          | Adopted   |
| Confidence intervals       | `utils/confidence.py`        | `app/utils/confidence.py`       | Adopted   |
| Health check endpoint      | `api/health.py`              | `app/api/v1/health.py`          | Adopted   |
| Docker Compose structure   | `docker-compose.yml`         | `docker-compose.yml`            | Adapted   |

### Modules Requiring Significant Adaptation

| Module                    | Changes Needed                                     |
|---------------------------|----------------------------------------------------|
| Scoring engine            | Replace geopolitical risk with sales risk factors   |
| Agent orchestrator        | Replace crisis agents with sales agents             |
| Dashboard components      | Replace map-centric with sales pipeline views       |
| Ingestion pipeline        | Add deduplication, quality scoring, Indian context  |

### Modules Removed (see removal-list.md)

All modules related to conflict tracking, military analysis, humanitarian crisis
monitoring, and geopolitical risk scoring have been completely removed.

## Code Quality Assessment

| Metric                    | WorldMonitor | SalesEdge Target |
|---------------------------|-------------|------------------|
| Type coverage             | ~60%        | 90%+             |
| Test coverage             | ~45%        | 80%+             |
| Lint compliance (ruff)    | Partial     | 100%             |
| API documentation         | Minimal     | Full OpenAPI     |

## Recommendations

1. Adopt the connector pattern and base class — well-tested and extensible.
2. Keep the cache manager architecture (3-tier) but add Redis sentinel support.
3. Rebuild all scoring engines from scratch with sales-specific features.
4. Rewrite all agents with new personas and domain knowledge.
5. Replace the frontend entirely with the SalesEdge "Warm Enterprise" design system.
