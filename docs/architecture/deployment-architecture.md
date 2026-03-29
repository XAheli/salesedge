# Deployment Architecture

## Docker Compose Topology

SalesEdge runs as four containers orchestrated by Docker Compose. All services share a
dedicated bridge network (`salesedge`) and communicate via container DNS names.

```
┌─────────────────────────────────────────────────────┐
│                   Host machine                      │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌───────┐  │
│  │ frontend │  │ backend  │  │ redis │  │ postgres│ │
│  │  :5173   │──│  :8000   │──│ :6379 │  │ :5432  │  │
│  └──────────┘  └──────────┘  └───────┘  └────────┘  │
│       ▲              ▲                               │
│       └──── salesedge bridge network ────────────────│
└─────────────────────────────────────────────────────┘
```

## Container Details

| Container   | Image                 | Port Mapping | Depends On       |
|-------------|-----------------------|-------------|------------------|
| `postgres`  | `postgres:16-alpine`  | 5432:5432   | —                |
| `redis`     | `redis:7-alpine`      | 6379:6379   | —                |
| `backend`   | `./backend/Dockerfile`| 8000:8000   | postgres, redis  |
| `frontend`  | `./frontend/Dockerfile`| 5173:5173  | backend          |

## Networking

All containers join the `salesedge` bridge network. Internal DNS resolves container
names automatically — the backend connects to PostgreSQL at `postgres:5432` and
Redis at `redis:6379` without needing IP addresses.

The frontend proxies `/api/*` requests to `http://backend:8000` via Vite's dev proxy
(development) or nginx reverse proxy (production).

## Health Checks

| Service    | Method | Endpoint / Command                              | Interval | Timeout | Retries |
|------------|--------|------------------------------------------------|----------|---------|---------|
| PostgreSQL | shell  | `pg_isready -U salesedge`                       | 5s       | 5s      | 5       |
| Redis      | shell  | `redis-cli ping`                                | 5s       | 3s      | 5       |
| Backend    | HTTP   | `GET /api/v1/health`                            | 15s      | 10s     | 5       |
| Frontend   | HTTP   | `fetch('http://127.0.0.1:5173')`                | 15s      | 10s     | 5       |

## Volume Mounts

| Volume              | Purpose                          | Persistence       |
|---------------------|----------------------------------|--------------------|
| `postgres_dev_data` | PostgreSQL data directory         | Named volume       |
| `redis_dev_data`    | Redis append-only file            | Named volume       |
| `./backend:/app`    | Live reload for backend code      | Bind mount (dev)   |
| `./frontend:/app`   | Live reload for frontend code     | Bind mount (dev)   |

## Environment Variable Flow

1. `.env` at repo root is loaded by Docker Compose via `env_file`.
2. The `backend` service overrides `SE_DATABASE_URL` and `SE_REDIS_URL` to use
   container DNS names (`postgres`, `redis`) instead of `localhost`.
3. The `frontend` service receives `VITE_API_BASE_URL` for API connectivity.

## Production Considerations

- Replace bind mounts with `COPY` in Dockerfiles (already the default for `docker compose --profile prod`).
- Add TLS termination at the nginx layer or use an external load balancer.
- Scale the backend horizontally: `docker compose up --scale backend=3` behind nginx.
- Externalize PostgreSQL and Redis to managed services (RDS, ElastiCache) for HA.
