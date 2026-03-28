# SalesEdge Documentation

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

Welcome to the SalesEdge documentation library. This index follows the master documentation structure (Section 13): architecture, data, scoring formulas, quality assurance, operations, development, end-user guidance, legal, and project governance.

---

## 1. Architecture

| Document | Description |
|----------|-------------|
| [Architecture overview](architecture/overview.md) | System context, containers, technology stack, key decisions, high-level data flow |
| [Data flow](architecture/data-flow.md) | Ingestion pipeline, caching tiers, bootstrap hydration, schedule by tier |
| [Agent architecture](architecture/agent-architecture.md) | Specialized agents, orchestrator, signal routing, action engine, lifecycle |

## 2. Data sources

| Document | Description |
|----------|-------------|
| [Data source catalog](data-sources/catalog.md) | All external APIs: tiers, auth, limits, endpoints, use cases, implementation status |
| [Government APIs](data-sources/government-apis.md) | OGD India, RBI DBIE, MOSPI, MCA, SEBI — usage and integration patterns |
| [Connector matrix](data-sources/connector-matrix.md) | Endpoint × business use-case coverage |

## 3. Formulas & scoring

| Document | Description |
|----------|-------------|
| [Formula handbook](formulas/handbook.md) | Prospect fit, deal risk, churn hazard, revenue recovery — full specification |
| [Prospect fit score](formulas/prospect-fit-score.md) | ICP fit methodology |
| [Deal risk score](formulas/deal-risk-score.md) | Pipeline risk methodology |
| [Churn hazard](formulas/churn-hazard.md) | Retention / churn methodology |

## 4. Testing

| Document | Description |
|----------|-------------|
| [Testing strategy](testing/strategy.md) | Pyramid, coverage targets, quality gates, tools |
| [Test matrix](testing/test-matrix.md) | Component × test type × status |

## 5. Operations

| Document | Description |
|----------|-------------|
| [Deployment guide](operations/deployment-guide.md) | Prerequisites through post-deploy verification |
| [Runbook](operations/runbook.md) | Day-2 tasks, troubleshooting, escalation |
| [Monitoring guide](operations/monitoring-guide.md) | Metrics, dashboards, alerts |
| [Secret management](operations/secret-management.md) | `SE_` variables, rotation, environments |

## 6. Development

| Document | Description |
|----------|-------------|
| [Local setup](development/setup.md) | Toolchains, Make targets, env reference |
| [Coding standards](development/coding-standards.md) | Python, TypeScript, Git, Indian formatting |
| [Adding a data source](development/adding-data-source.md) | Connectors, registry, tests |

## 7. User guide

| Document | Description |
|----------|-------------|
| [Getting started](user-guide/getting-started.md) | First login, dashboard, navigation, concepts |
| [Executive cockpit](user-guide/executive-cockpit.md) | KPIs, charts, time windows, export |

## 8. Legal & compliance

| Document | Description |
|----------|-------------|
| [Third-party notices](legal/THIRD_PARTY_NOTICES.md) | Open-source acknowledgements |
| [Data usage compliance](legal/DATA_USAGE_COMPLIANCE.md) | Government and public data terms |

## 9. Project governance

| Resource | Description |
|----------|-------------|
| [Contributing](../CONTRIBUTING.md) | How to contribute to SalesEdge |
| [Changelog](../CHANGELOG.md) | Release history |
| [Repository README](../README.md) | Quick start and repository overview |

---

*Last updated: March 2026.*
