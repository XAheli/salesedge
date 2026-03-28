# Coding Standards

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Adding a data source](adding-data-source.md)

---

## Python

| Topic | Standard |
|-------|----------|
| Lint / format | **Ruff** (`ruff check`, `ruff format`) — see `pyproject.toml` |
| Types | **mypy strict** on `app` |
| Schemas | **Pydantic v2** for settings and API models |
| Async | Prefer `async def` for I/O; use `httpx.AsyncClient` in connectors |
| Logging | **structlog** JSON-friendly keys |

Run `make lint` and `make typecheck` before pushing.

## TypeScript

| Topic | Standard |
|-------|----------|
| Lint | **ESLint** + TypeScript rules (`npm run lint`) |
| Format | **Prettier** (`npm run format`) |
| Compiler | **strict** mode in `tsconfig.json` |
| Data fetching | TanStack Query patterns; avoid unhandled promise rejections |

## Git

- **Atomic commits** — one logical change per commit when possible.  
- **Conventional Commits** — e.g. `feat(connectors): add MOSPI health check`, `fix(api): correct JWT expiry`.  
- PRs should describe motivation, scope, and risk.

## Indian formatting

Always surface currency and local time consistently (product convention: **formatINR** / **formatIST**; code uses snake_case on the backend):

| Context | Use |
|---------|-----|
| Backend INR | `format_inr` from `app/utils/indian_formats.py` |
| Frontend INR | **`formatINR`** from `frontend/src/utils/indian-formatting.ts` |
| Timestamps | **`formatIST`** from `frontend/src/utils/indian-formatting.ts` (and `ISTTimestamp` component) |

Do not hardcode `USD` or a single global timezone for user-visible sales data.

---

[← Documentation index](../README.md)
