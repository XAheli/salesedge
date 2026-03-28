# Test Matrix

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Testing strategy](strategy.md)

---

**Status legend:** ✅ active · 🔄 planned · ⏸️ skipped (environment)  

| Component | Unit | Integration | Contract | E2E | Performance |
|-----------|------|-------------|----------|-----|-------------|
| `BaseConnector` / circuit breaker | ✅ | ⏸️ | — | — | — |
| Government connectors (OGD, RBI, …) | ✅ | 🔄 | 🔄 | — | — |
| Market / broker connectors | ✅ | 🔄 | 🔄 | — | — |
| Enrichment (Finnhub, FMP, …) | ✅ | 🔄 | 🔄 | — | — |
| Ingestion pipeline / normalization | 🔄 | 🔄 | — | — | — |
| Feature store | 🔄 | 🔄 | — | — | — |
| Prospect / deal / churn / recovery scoring | ✅ | 🔄 | — | — | — |
| Agents + orchestrator | 🔄 | 🔄 | — | — | — |
| FastAPI routers (`/api/v1/*`) | ✅ | 🔄 | 🔄 | — | ✅ |
| Auth / JWT dependencies | ✅ | 🔄 | — | 🔄 | — |
| React dashboard shell | 🔄 | — | — | 🔄 | — |
| Executive cockpit charts | 🔄 | — | — | 🔄 | 🔄 |
| Indian formatting (`format_inr`, `formatIST`) | ✅ | — | — | — | — |
| Cache manager (L1/L2) | ✅ | 🔄 | — | — | ✅ |

> Matrix reflects roadmap maturity: expand 🔄 cells as suites land in CI.

---

[← Documentation index](../README.md)
