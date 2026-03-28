# Third-Party Notices

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md)

---

SalesEdge incorporates open-source software. Below is a non-exhaustive acknowledgement of major components. See `backend/pyproject.toml`, `backend/requirements.txt`, and `frontend/package.json` for complete dependency manifests and versions at build time.

## Backend (Python)

| Project | License (typical) | Use |
|---------|-------------------|-----|
| FastAPI | MIT | HTTP API framework |
| Uvicorn | BSD | ASGI server |
| Pydantic / pydantic-settings | MIT | Validation and settings |
| SQLModel / SQLAlchemy | MIT | ORM and database access |
| asyncpg | Apache-2.0 | PostgreSQL async driver |
| Redis (redis-py) | MIT | Cache and pub/sub client |
| httpx | BSD-3-Clause | Async HTTP client |
| tenacity | Apache-2.0 | Retries |
| structlog | MIT / dual | Structured logging |
| scikit-learn | BSD-3-Clause | ML models |
| pandas / polars / pyarrow | BSD-3-Clause / MIT | Data processing |
| DuckDB | MIT | Embedded analytics |
| Alembic | MIT | Database migrations |
| prometheus-client | Apache-2.0 | Metrics exposition |
| python-jose | MIT | JWT handling |
| beautifulsoup4 / lxml | MIT | HTML parsing for government sources |

## Frontend (TypeScript / JavaScript)

| Project | License (typical) | Use |
|---------|-------------------|-----|
| React | MIT | UI library |
| Vite | MIT | Build tool |
| TypeScript | Apache-2.0 | Language |
| TanStack Query | MIT | Server state |
| Zustand | MIT | Client state |
| Axios | MIT | HTTP client |
| Tailwind CSS | MIT | Styling |
| Radix UI | MIT | Accessible primitives |
| Nivo / Recharts / D3 | MIT | Charts |
| Vitest / Testing Library | MIT | Testing |
| ESLint / Prettier | MIT | Lint and format |

## Full license texts

Retrieve SPDX license texts from [https://spdx.org/licenses/](https://spdx.org/licenses/) or vendor `LICENSE` files inside `node_modules` and Python site-packages for the exact version shipped.

---

[← Documentation index](../README.md)
