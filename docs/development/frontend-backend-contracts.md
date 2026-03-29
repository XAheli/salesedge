# Frontend-Backend API Contracts

## Principle

The frontend and backend must agree on the exact shape of API request and response
payloads. SalesEdge enforces this through shared type definitions and automated
contract tests.

## Type Synchronization

### Backend (Source of Truth)

Pydantic v2 schemas in `backend/app/schemas/` define the canonical API models:

```
backend/app/schemas/
├── common.py          # PaginatedResponse, ErrorResponse
├── dashboard.py       # KPIResponse, PipelineFunnel
├── prospects.py       # ProspectList, ProspectDetail, FitScoreBreakdown
├── deals.py           # DealList, DealDetail, RiskWaterfall
├── retention.py       # RetentionOverview, ChurnRiskTable
├── competitive.py     # SignalFeed, Battlecard
├── data_sources.py    # SourceStatus, QualityScore
└── signals.py         # SignalList, SignalDetail
```

### Frontend (Derived Types)

TypeScript interfaces in `frontend/src/types/` mirror the Pydantic schemas.
The `scripts/generate-types.sh` script automates this:

```bash
# Generate TypeScript types from the running backend's OpenAPI spec
./scripts/generate-types.sh
```

This script:

1. Fetches `/openapi.json` from the running backend.
2. Runs `openapi-typescript` to generate `frontend/src/types/api.generated.ts`.
3. Developers import from the generated file rather than hand-writing interfaces.

### Manual Type Alignment

When `generate-types.sh` isn't being used, maintain types manually by following
these conventions:

| Pydantic Field     | TypeScript Equivalent       | Notes                     |
|--------------------|-----------------------------|---------------------------|
| `str`              | `string`                    |                           |
| `int`              | `number`                    |                           |
| `float`            | `number`                    |                           |
| `bool`             | `boolean`                   |                           |
| `datetime`         | `string` (ISO 8601)         | Parsed with `date-fns`   |
| `Optional[T]`     | `T \| null`                 |                           |
| `list[T]`          | `T[]`                       |                           |
| `dict[str, T]`     | `Record<string, T>`         |                           |

## Contract Tests

Automated tests in `backend/tests/contract/` verify that API responses match the
declared Pydantic schemas:

### `test_api_contracts.py`

- Hits every API endpoint via `httpx.AsyncClient`.
- Validates the response body against the expected Pydantic model using
  `model_validate`.
- Catches regressions where the backend returns extra/missing fields.

### `test_external_api_schemas.py`

- Fetches sample responses from upstream APIs (Finnhub, Alpha Vantage, etc.).
- Validates against expected schemas to detect upstream API drift.
- Uses mocked responses for CI, live responses for nightly runs.

## Adding a New Endpoint

1. **Backend:** Define the Pydantic response schema in `backend/app/schemas/`.
2. **Backend:** Implement the endpoint in `backend/app/api/v1/`.
3. **Contract test:** Add a test in `test_api_contracts.py` that calls the endpoint
   and validates the response shape.
4. **Frontend:** Run `./scripts/generate-types.sh` or manually add the TypeScript
   interface to `frontend/src/types/`.
5. **Frontend:** Implement the API call in `frontend/src/api/` using `axios` with
   the typed response.

## Breaking Change Policy

- **Additive changes** (new optional fields) are non-breaking — no version bump needed.
- **Removals or renames** require a deprecation period: return both old and new fields
  for at least one release cycle.
- **Type changes** (e.g., `int` → `string`) are always breaking — bump the API
  version (`/api/v2/`) or negotiate with the frontend team.
