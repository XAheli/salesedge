# SalesEdge Remaining Work Backlog (Masterprompt Gap Audit)

Generated: 2026-03-29  
Baseline: `masterprompt.md`  
Audit mode: repository-wide structure check plus targeted code-level parity checks

## 1. Scope And Interpretation

This document lists what is still left to complete against `masterprompt.md`.

What this audit covers:
- Required repository structure and required artifacts in `masterprompt.md` Section 6
- API contract and cross-layer parity (backend schemas/routes vs frontend client/hooks/types)
- Backend implementation completeness for required endpoints and websocket layer
- Frontend chart catalog and wrapper/accessibility requirements
- Testing and operational readiness artifacts
- Section 7 sub-agent deliverables and inputs

What this audit does not claim:
- Full functional correctness of every existing module
- Exact production SLA/performance conformance without running complete perf suites

---

## 2. Critical Priority Backlog (P0)

These items block strict compliance and should be completed first.

### P0-1. Fix API contract envelope drift (`meta` vs `metadata` + type drift)

Affected files:
- `backend/app/schemas/common.py`
- `frontend/src/types/api/common.ts`
- `frontend/src/api/client.ts`
- all `backend/app/api/v1/*.py` routes returning envelopes

Current gap:
- Backend envelope field is `meta`; frontend expects `metadata`.
- Backend `SourceAttribution.reliability_tier` is `int` (1-3); frontend expects string union (`tier1|tier2|tier3`).
- Backend `PaginatedResponse` includes `meta`; frontend `PaginatedResponse` type has no metadata field.
- Backend `cache_status` accepts free-form string; frontend expects constrained union.

Required action:
1. Define a single canonical envelope contract in backend and frontend.
2. Regenerate/align frontend API types from backend OpenAPI (or change backend to match TS types exactly).
3. Add contract tests to prevent future drift.

Acceptance criteria:
- All frontend hooks compile with strict types and no `any` fallbacks.
- Contract test suite validates envelope shape for success and error responses.
- One documented contract location exists and both layers match exactly.

### P0-2. Implement missing backend routes that frontend already calls

Affected files:
- Missing: `backend/app/api/v1/search.py`
- Missing: `backend/app/api/v1/admin.py`
- Existing but incomplete: `backend/app/api/v1/retention.py`
- Existing but incomplete: `backend/app/api/v1/competitive.py`
- `backend/app/api/v1/router.py`
- `frontend/src/api/hooks/useSearch.ts`
- `frontend/src/api/hooks/useRetention.ts`
- `frontend/src/api/hooks/useCompetitive.ts`

Current gap:
- Frontend calls `/v1/search`, but backend search router file is missing.
- Frontend retention hooks call `/cohorts`, `/churn-predictions`, `/customers/{id}/health`; backend exposes only `/overview`.
- Frontend competitive hooks call `/mentions`, `/battlecards`, `/policy-signals`, `/market-signals`; backend exposes only `/overview`.

Required action:
1. Add missing `search` and `admin` routers.
2. Implement retention and competitive endpoint coverage expected by frontend.
3. Register all new routers in `backend/app/api/v1/router.py`.

Acceptance criteria:
- No frontend 404s for hook endpoints.
- OpenAPI includes all required v1 routes.
- Integration tests pass for search, retention, and competitive route families.

### P0-3. Implement websocket backend expected by frontend

Affected files:
- `backend/app/api/websocket/.gitkeep` (only placeholder exists)
- Missing: `backend/app/api/websocket/manager.py`
- Missing: `backend/app/api/websocket/deal_alerts.py`
- Missing: `backend/app/api/websocket/data_updates.py`
- `backend/app/main.py`
- `frontend/src/api/websocket/useAlerts.ts`
- `frontend/src/api/websocket/useDataUpdates.ts`

Current gap:
- Frontend expects websocket paths `/ws/alerts` and `/ws/data-updates`.
- Backend websocket implementation files are absent.

Required action:
1. Implement websocket connection manager.
2. Add alert and data update websocket routes.
3. Wire websocket routes into FastAPI app.

Acceptance criteria:
- Frontend websocket hooks connect successfully without fallback errors.
- Realtime updates can be validated end-to-end in local/dev environment.

### P0-4. Resolve auth token key mismatch

Affected files:
- `frontend/src/pages/Login.tsx`
- `frontend/src/api/client.ts`

Current gap:
- Login stores token in `salesedge-token`.
- API client reads/removes `salesedge_token`.

Required action:
1. Standardize to one key name.
2. Add one regression test for auth persistence behavior.

Acceptance criteria:
- Login session persists and authenticated API requests include bearer token.
- Logout/401 cleanup removes the same key that login sets.

### P0-5. Remove placeholder data provenance freshness values

Affected files:
- `backend/app/api/v1/data_provenance.py`
- `backend/app/schemas/data_sources.py`

Current gap:
- Freshness strings are hardcoded human text (for example "24 hours ago").
- No computed freshness derived from ingestion timestamps.

Required action:
1. Source freshness from real ingestion metadata or source snapshots.
2. Provide deterministic freshness computation and standardized formatting.

Acceptance criteria:
- Freshness values are generated from real timestamps, not literals.
- Data provenance tests assert freshness derivation logic.

### P0-6. Finish connector implementations currently stubbed with `NotImplementedError`

Affected files:
- `backend/app/connectors/broker/upstox.py`
- `backend/app/connectors/broker/fyers.py`
- `backend/app/connectors/broker/icici_breeze.py`
- `backend/app/connectors/broker/angelone.py`
- `backend/app/connectors/crypto/binance.py`
- `backend/app/connectors/enrichment/fx/exchangerate_host.py`

Current gap:
- Connectors contain explicit `raise NotImplementedError(...)` placeholders.

Required action:
1. Implement connector methods according to connector interface and retry/cache policy.
2. Add unit tests using mocked upstream responses.

Acceptance criteria:
- No production-path connector raises `NotImplementedError`.
- Connector health checks and schema validations pass.

### P0-7. Fix score scale inconsistency for deal risk (0-1 vs 0-100)

Affected files:
- `backend/app/models/deal.py`
- `backend/app/schemas/deals.py`
- `backend/app/api/v1/deals.py`
- `backend/app/fetch_real_data.py`
- `frontend/src/api/hooks/useDeals.ts`

Current gap:
- Data model and schemas constrain `risk_score` to 0-100.
- Seed generation in `fetch_real_data.py` writes 0-1 values.
- Different route/page logic uses different thresholds (0.7 style and 80/60/30 style), creating semantic ambiguity.

Required action:
1. Select one canonical scale for `risk_score` across model, schemas, seeders, services, and UI.
2. Normalize historical data and adapt thresholds accordingly.
3. Add explicit conversion helper only if mixed-source ingestion requires it.

Acceptance criteria:
- One documented risk score scale used system-wide.
- All thresholds and chart legends match that scale.
- Tests verify consistent behavior for boundary values.

---

## 3. High Priority Backlog (P1)

### P1-1. Complete chart catalog from `masterprompt.md`

Missing chart components:
- `frontend/src/components/charts/OutreachPerformance.tsx`
- `frontend/src/components/charts/CalibrationCurve.tsx`
- `frontend/src/components/charts/ErrorDistribution.tsx`
- `frontend/src/components/charts/PrecisionRecall.tsx`
- `frontend/src/components/charts/APILatency.tsx`
- `frontend/src/components/charts/BacktestTracker.tsx`
- `frontend/src/components/charts/DecisionSimulator.tsx`

Current gap:
- 7 chart files required by prompt are missing.

Required action:
1. Implement missing chart components with shared chart style/theme.
2. Add component tests and accessibility checks.

Acceptance criteria:
- Required chart files exist and are used in pages where specified.
- Each chart has loading, empty, and error states.

### P1-2. Enforce standard chart wrapper usage

Affected files:
- `frontend/src/components/charts/ChartContainer.tsx`
- all chart usage sites across `frontend/src/pages/*.tsx`

Current gap:
- `ChartContainer` exists but is not used by chart pages.
- Prompt requires every chart wrapped in standard metadata/export/time-window container.

Required action:
1. Wrap all charts with `ChartContainer`.
2. Wire metadata, export, and time-window controls consistently.

Acceptance criteria:
- No raw chart render without `ChartContainer`.
- Chart metadata is visible and test-covered.

### P1-3. Add accessibility text alternatives for charts

Affected files:
- `frontend/src/components/charts/*.tsx`
- `frontend/src/pages/*.tsx`

Current gap:
- Prompt requires chart text alternatives via `<details>` summaries.
- No `<details>` usage found in chart/pages scan.

Required action:
1. Add text summary per chart.
2. Ensure keyboard focus and screen reader labeling for chart controls.

Acceptance criteria:
- Accessibility checks verify each chart has textual alternative.
- Keyboard-only navigation covers chart interactions.

### P1-4. Add missing backend middleware artifacts from structure baseline

Missing files:
- `backend/app/api/middleware/auth.py`
- `backend/app/api/middleware/cache.py`
- `backend/app/api/middleware/audit_log.py`

Required action:
1. Implement auth/cache/audit middleware modules or explicitly document merged behavior into existing middleware stack.
2. Ensure registration in app factory and route policy mapping.

Acceptance criteria:
- Middleware behavior is test-covered and documented.
- No required middleware file missing from baseline structure.

### P1-5. Fix Makefile script reference drift

Affected files:
- `Makefile`
- Missing script path currently referenced: `backend/scripts/build-connector-matrix.py`
- Missing expected script from prompt: `scripts/build-connector-matrix.py`

Current gap:
- Make target points to non-existent backend path.

Required action:
1. Implement script at canonical location.
2. Update Makefile target to correct path.

Acceptance criteria:
- `make connector-matrix` works from clean checkout.

---

## 4. Structure Compliance: Verified Missing Artifacts (67)

The following paths were explicitly checked and are currently missing.

### 4.1 Docs

- `docs/architecture/deployment-architecture.md`
- `docs/architecture/diagrams/system-context.mmd`
- `docs/architecture/diagrams/container-diagram.mmd`
- `docs/architecture/diagrams/data-flow.mmd`
- `docs/architecture/diagrams/agent-orchestration.mmd`
- `docs/data-sources/market-apis.md`
- `docs/data-sources/enrichment-apis.md`
- `docs/data-sources/compliance-notes.md`
- `docs/formulas/revenue-recovery-priority.md`
- `docs/formulas/calibration-methods.md`
- `docs/api/openapi.yaml`
- `docs/api/postman-collection.json`
- `docs/testing/backtesting-guide.md`
- `docs/operations/rollback-plan.md`
- `docs/operations/backup-restore.md`
- `docs/user-guide/prospect-intelligence.md`
- `docs/user-guide/deal-risk-console.md`
- `docs/user-guide/retention-churn.md`
- `docs/user-guide/competitive-intelligence.md`
- `docs/user-guide/data-provenance.md`
- `docs/development/frontend-backend-contracts.md`

### 4.2 Backend

- `backend/requirements-dev.txt`
- `backend/app/api/middleware/auth.py`
- `backend/app/api/middleware/cache.py`
- `backend/app/api/middleware/audit_log.py`
- `backend/app/api/v1/search.py`
- `backend/app/api/v1/admin.py`
- `backend/app/api/websocket/manager.py`
- `backend/app/api/websocket/deal_alerts.py`
- `backend/app/api/websocket/data_updates.py`
- `backend/tests/contract/test_api_contracts.py`
- `backend/tests/contract/test_external_api_schemas.py`
- `backend/tests/integration/test_ingestion_pipeline.py`
- `backend/tests/integration/test_api_endpoints.py`
- `backend/tests/integration/test_agent_orchestration.py`
- `backend/tests/integration/test_data_flow.py`
- `backend/tests/performance/locustfile.py`
- `backend/tests/e2e/test_critical_paths.py`
- `backend/tests/backtesting/test_historical_replay.py`

Note:
- `backend/uv.lock` is present.

### 4.3 Frontend

- `frontend/public/logo-dark.svg`
- `frontend/public/manifest.json`
- `frontend/.eslintrc.cjs`
- `frontend/.prettierrc`
- `frontend/tests/e2e/playwright.config.ts`
- `frontend/tests/e2e/specs/dashboard-flow.spec.ts`
- `frontend/tests/e2e/specs/prospect-workflow.spec.ts`
- `frontend/tests/e2e/specs/deal-risk-flow.spec.ts`

### 4.4 Root Scripts

- `scripts/run-backtests.sh`
- `scripts/rotate-keys.sh`
- `scripts/build-connector-matrix.py`

### 4.5 Data Seeds And Schemas

- `data/seed/prospects.json`
- `data/seed/deals.json`
- `data/seed/signals.json`
- `data/seed/indian_companies.json`
- `data/schemas/ogd_dataset_registry.json`
- `data/schemas/connector_matrix.json`

### 4.6 Infra

- `infra/docker/backend.Dockerfile`
- `infra/docker/frontend.Dockerfile`
- `infra/docker/redis/redis.conf`
- `infra/k8s/namespace.yaml`
- `infra/k8s/backend-deployment.yaml`
- `infra/k8s/frontend-deployment.yaml`
- `infra/k8s/redis-deployment.yaml`
- `infra/k8s/postgres-deployment.yaml`
- `infra/k8s/ingress.yaml`

### 4.7 VS Code Workspace Artifacts

- `.vscode/settings.json`
- `.vscode/launch.json`

---

## 5. Testing Maturity Gaps

Placeholder-only test areas found:
- `backend/tests/contract/.gitkeep`
- `backend/tests/integration/.gitkeep`
- `backend/tests/e2e/.gitkeep`
- `backend/tests/performance/.gitkeep`
- `backend/tests/backtesting/historical_data/.gitkeep`
- `frontend/tests/e2e/specs/.gitkeep`
- `frontend/tests/hooks/.gitkeep`
- `frontend/tests/pages/.gitkeep`

Required action:
1. Replace placeholders with real tests matching `docs/testing/test-matrix.md` targets.
2. Enforce CI gates for unit, integration, contract, e2e, and performance smoke suites.

Acceptance criteria:
- CI fails when contract drift or critical endpoint regressions occur.
- E2E tests cover dashboard, prospect workflow, and deal risk flow paths.

---

## 6. Section 7 Sub-Agent Deliverable Gaps

Missing migration artifacts required by prompt:
- `docs/migration/repo-audit.md`
- `docs/migration/reusable-modules.md`
- `docs/migration/removal-list.md`
- `docs/migration/migration-plan.md`

Missing source inputs expected by sub-agent tasks:
- `available_api/api_info.csv`
- `available_api/available_api.json`

Required action:
1. Produce required migration artifacts under `docs/migration/`.
2. Add or source `available_api` inventory files, or adjust spec and document equivalent source of truth.

Acceptance criteria:
- Section 7 deliverables exist and are reviewable.
- Data-source agent can produce connector matrix from available inputs.

---

## 7. Sequenced Execution Plan

### Phase 1 (Stabilize Contracts And Runtime)

1. Fix token key mismatch.
2. Align API envelope contract (`meta`/`metadata`, tier typing, paginated metadata).
3. Implement missing search/admin routes.
4. Implement websocket manager + endpoints and wire into app.
5. Normalize deal risk score scale across data model, seeders, backend logic, and UI.

### Phase 2 (Close Feature Coverage)

1. Implement retention and competitive endpoint families required by frontend hooks.
2. Replace connector stubs with production-ready implementations.
3. Replace hardcoded provenance freshness with computed values.
4. Complete missing chart components and enforce `ChartContainer` wrapper usage.
5. Add chart text alternatives and accessibility coverage.

### Phase 3 (Testing, Docs, Operations)

1. Populate missing test suites and e2e flows.
2. Add missing docs artifacts (API, formulas, operations, user guides, architecture diagrams).
3. Add missing infra assets (docker overlays, k8s manifests, redis config).
4. Add missing scripts and correct Makefile wiring.
5. Add `.vscode` workspace files and finalize developer workflow docs.

---

## 8. Definition Of Done Checklist

- [ ] Frontend and backend contracts are generated/synced from one source.
- [ ] No missing P0 route or websocket endpoint called by frontend.
- [ ] No production connector raises `NotImplementedError`.
- [ ] Risk score scale is single-source and consistent everywhere.
- [ ] All required chart modules exist and are wrapped in `ChartContainer`.
- [ ] Accessibility requirements (including chart text alternatives) are implemented and tested.
- [ ] Missing structure artifacts are created or intentionally waived with explicit rationale.
- [ ] Contract, integration, e2e, and performance smoke tests are present and passing in CI.

---

## 9. Immediate Next 10 Tasks (Recommended)

1. Standardize token storage key in frontend auth flow.
2. Decide and codify canonical response envelope naming and metadata types.
3. Implement `backend/app/api/v1/search.py` and wire router.
4. Implement websocket manager and `/ws/alerts`, `/ws/data-updates`.
5. Add missing retention routes used by `useRetention.ts`.
6. Add missing competitive routes used by `useCompetitive.ts`.
7. Normalize `risk_score` scale and migrate seeded data generation.
8. Add `scripts/build-connector-matrix.py` and fix `Makefile` target path.
9. Create backend contract/integration test files replacing placeholder dirs.
10. Create `docs/development/frontend-backend-contracts.md` and `docs/api/openapi.yaml` generation flow.
