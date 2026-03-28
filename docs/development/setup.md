# Local Development Setup

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Coding standards](coding-standards.md)

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|--------|
| Python | **3.12+** | Matches `requires-python` in `backend/pyproject.toml` |
| Node.js | **20.x** | For Vite/React frontend |
| Docker | Current | Postgres + Redis |
| uv | Latest (optional) | Makefile `dev-backend` uses `uv run`; bootstrap may use pip |

## Bootstrap

From the repository root:

```bash
make bootstrap
```

This runs `scripts/bootstrap.sh`: creates `backend/.venv`, installs Python deps, `npm install` in `frontend`, copies `.env.example` → `.env`, starts Postgres/Redis via `docker-compose.yml`, runs Alembic, seeds data.

## Running the backend

```bash
make dev-backend
```

Runs Uvicorn with reload on `http://0.0.0.0:8000`. Ensure `SE_OGD_API_KEY` and DB URL are set.

## Running the frontend

```bash
make dev-frontend
```

Vite dev server (default `http://localhost:5173`). `VITE_API_BASE_URL` should point at the API.

## Full stack via Compose

**Infrastructure only (API/UI on host):**

```bash
make dev
```

Uses `docker-compose.dev.yml` (Postgres + Redis). Then run `make dev-backend` and `make dev-frontend` in separate terminals.

**Everything in Docker:**

```bash
docker compose up --build
```

## Environment variable reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SE_DATABASE_URL` | Yes (non-default) | `postgresql+asyncpg://...` |
| `SE_REDIS_URL` | Yes (non-default) | Redis URL |
| `SE_OGD_API_KEY` | Yes | Government data portal |
| `SE_JWT_SECRET_KEY` | Prod | Auth signing |
| `SE_*` | Per connector | See `app/config.py` |

Compose sets `SE_DATABASE_URL` / `SE_REDIS_URL` for the `backend` service when using bundled files.

---

[← Documentation index](../README.md)
