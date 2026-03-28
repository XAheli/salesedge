# Deployment Guide

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Runbook](runbook.md) · [Secret management](secret-management.md)

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Docker & Docker Compose | v20+ / v2+ recommended |
| API keys | At minimum `SE_OGD_API_KEY`; others per enabled connectors |
| TLS certificates (production) | Mounted under `infra/docker/nginx/ssl` for `docker-compose.prod.yml` |
| Resource sizing | Postgres + Redis + API + nginx — size vCPU/RAM to peak connector fan-out |

## Environment setup

1. Copy `.env.example` → `.env` at repository root.  
2. Set `SE_DATABASE_URL` for async SQLAlchemy: `postgresql+asyncpg://user:pass@host:5432/salesedge`.  
3. Set `SE_REDIS_URL`, `SE_JWT_SECRET_KEY` (strong random in prod), and connector keys (`SE_*`).  
4. See [secret-management.md](secret-management.md) for naming rules.

## Database migration

From `backend/` with venv active:

```bash
alembic upgrade head
```

`scripts/bootstrap.sh` runs this after Postgres is healthy.

## Docker Compose deployment

**Production-shaped stack:**

```bash
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

**Full local stack (API + UI + DB + Redis):**

```bash
docker compose up -d --build
```

Compose files: `docker-compose.yml` (dev services), `docker-compose.prod.yml` (nginx + TLS).

## Health verification

| Check | Command / URL |
|-------|----------------|
| API | `GET http://<host>:8000/api/v1/health` (or through nginx) |
| Postgres | `pg_isready` inside container |
| Redis | `redis-cli ping` |
| Frontend | HTTP 200 on `/` |

## Post-deploy checks

- [ ] Connector registry health (planned admin endpoint or logs).  
- [ ] Sample authenticated API call succeeds.  
- [ ] Dashboard loads with IST/INR formatting.  
- [ ] `make check-freshness` or scheduled freshness job passes SLAs.  
- [ ] Log aggregation receiving structured logs (`structlog`).

---

[← Documentation index](../README.md)
