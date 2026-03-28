# Testing Strategy

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Test matrix](test-matrix.md)

---

## Test pyramid

```
                    ┌─────────────┐
                    │  E2E (few)  │  Playwright — critical user journeys
                    └──────┬──────┘
               ┌───────────┴───────────┐
               │ Contract + Integration │  pytest — API & DB boundaries
               └───────────┬───────────┘
          ┌─────────────────┴─────────────────┐
          │            Unit (many)             │  pytest / Vitest — pure logic
          └───────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │ Performance (Locust) │  Soak / SLA validation (select builds)
                    └───────────────────┘
```

## Coverage targets

| Area | Line/branch target | Notes |
|------|---------------------|--------|
| Backend | **≥ 80%** | Focus on connectors, scoring, ingestion |
| Frontend | **≥ 70%** | Components, hooks, formatters |
| Critical paths | **≥ 95%** | Auth, scoring APIs, payment/churn decisions |

Use `pytest-cov` and Vitest `--coverage` in CI; fail builds below thresholds once baselines exist.

## Quality gates (Section 7 — Sub-Agent 6)

| Gate | Command / check | Blocking? |
|------|-----------------|-----------|
| Lint (Python) | `make lint` → `ruff check` | Yes |
| Lint (TS) | ESLint via `npm run lint` | Yes |
| Format | `make format` (optional auto-fix in CI with review) | Advisory or Yes |
| Types | `make typecheck` → `mypy --strict`, `tsc --noEmit` | Yes |
| Unit | `make test-unit` | Yes |
| Integration | `make test-integration` | Yes on `main` |
| Contract | `make test-contract` | Yes when API consumers exist |
| E2E | `make test-e2e` | Nightly or pre-release |
| Performance | `make test-performance` | Weekly / release candidate |
| Backtest | `make test-backtest` | When scoring models change |
| Security | Dependency audit (tool TBD in CI) | Yes for CVEs above threshold |

## Tool choices

| Tool | Scope |
|------|--------|
| **pytest** | Backend unit, integration, contract, backtests |
| **pytest-asyncio** | Async connectors and FastAPI routes |
| **Vitest** | Frontend unit/component tests |
| **Playwright** | Browser E2E (`make test-e2e`) |
| **Locust** | Load tests (`tests/performance/locustfile.py`) |
| **httpx** | In-process async client for API tests |

## Test data

- Prefer factories over fixtures duplicated across files.  
- **Never** commit real API keys; use `.env.test` or CI secrets.  
- CRM demos: `simulated_crm` connector for deterministic scenarios.

---

[← Documentation index](../README.md)
