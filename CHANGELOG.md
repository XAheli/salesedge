# Changelog

All notable changes to **SalesEdge — Intelligent Sales & Revenue Operations Platform** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-28

### Added

- Initial public documentation set under `docs/`: architecture, data sources, formulas, testing, operations, development, user guide, and legal notices.  
- FastAPI backend with async SQLModel/PostgreSQL, Redis-backed caching, connector framework with circuit breaker and retries, ingestion scheduling tiers, feature store modules, scoring engines (prospect fit, deal risk, churn, recovery priority), and multi-agent orchestration.  
- React (Vite) frontend with Indian formatting utilities (INR, IST) and dashboard-oriented dependencies.  
- Docker Compose definitions for local and production-style deployment, Makefile targets for bootstrap, dev servers, testing, and deployment scripts hooks.  
- CONTRIBUTING guidelines and compliance-oriented data usage notes for Indian government data sources.

### Notes

- Some connectors and integrations are documented as **stub** pending full implementation; see `docs/data-sources/catalog.md`.
