<p align="center">
  <img src="frontend/public/logo.svg" alt="SalesEdge" width="80" height="80" />
</p>

<h1 align="center">SalesEdge</h1>

<p align="center"><strong>Intelligent Sales & Revenue Operations Platform</strong></p>

An India-focused AI platform for enterprise sales teams. Integrates government data (data.gov.in, RBI, MOSPI, SEBI), Indian market data (NSE, BSE), and 25+ financial APIs to power prospect intelligence, deal risk scoring, churn prediction, and competitive analysis.


## How to Run Locally

### Prerequisites

You need these three tools installed on your system before starting. `make bootstrap` handles everything else.

- **Python 3.12+** — [python.org/downloads](https://www.python.org/downloads/) or your package manager
- **Node.js 20+** — [nodejs.org](https://nodejs.org/) or `nvm install 20`
- **Docker** — [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) (needed for PostgreSQL and Redis)

Verify all three:
```bash
python3 --version   # must show 3.12 or higher
node --version      # must show v20 or higher
docker --version    # any recent version
```

### Setup and Run

```bash
# 1. Clone the repository
git clone https://github.com/XAheli/salesedge.git
cd salesedge

# 2. First run — this creates .env and tells you to add your API keys
make bootstrap
#    On first run, it creates .env from the template and stops.
#    You MUST set your API keys before proceeding.

# 3. Add your API keys (open .env in any editor)
nano .env
#    REQUIRED — set this or the app won't start:
#      SE_OGD_API_KEY=<your key>     → get free at https://data.gov.in/help/apis
#
#    OPTIONAL — enables the AI Agents chat page:
#      SE_LLM_API_KEY=<your key>     → get free at https://openrouter.ai/keys

# 4. Run bootstrap again — now it installs everything
make bootstrap
#    Installs Python + Node deps, starts PostgreSQL & Redis,
#    runs migrations, seeds real NIFTY company data.

# 5. Start the backend (Terminal 1 — keep open)
make dev-backend
#    → http://localhost:8000 (API)
#    → http://localhost:8000/docs (Swagger)

# 6. Start the frontend (Terminal 2 — keep open)
make dev-frontend
#    → http://localhost:5173

# 7. Open http://localhost:5173
#    → Register → Dashboard with real data
```

### What `make bootstrap` does

1. Creates `.env` from template (first run only — then stops for you to add keys)
2. Validates `SE_OGD_API_KEY` is set (fails with clear message if not)
3. Installs `uv` (Python package manager) if missing
4. Creates `backend/.venv` and installs all Python dependencies
5. Installs frontend npm packages
6. Starts PostgreSQL 16 and Redis 7 via Docker Compose
7. Runs database migrations
8. Seeds database with **40 real NIFTY 50/100 companies**, deals, and **30 market signals**
9. Verifies data.gov.in API connectivity

---

## Pages

| URL | Page | What you'll see |
|-----|------|-----------------|
| `/` | Dashboard | KPIs (ARR, Pipeline, Win Rate), pipeline funnel, risk heatmap, top deals |
| `/prospects` | Prospects | Searchable table of 40+ real Indian companies with fit scores |
| `/deals` | Deals | Deal pipeline grouped by risk level: at-risk, healthy, won, lost |
| `/retention` | Retention | Churn analysis, risk distribution, loss reasons, at-risk accounts |
| `/intelligence` | Intelligence | Policy signals (RBI/SEBI), competitor funding, market trends |
| `/agents` | AI Agents | Chat interface with 4 AI agents (requires LLM API key) |
| `/data` | Data Provenance | API health status, data freshness, source connectivity |
| `/settings` | Settings | Profile, API keys, notifications, dark mode toggle |

---

## Make Commands Reference

| Command | Description |
|---------|-------------|
| `make bootstrap` | **Run first.** Full setup: installs deps, starts DB, seeds data |
| `make dev-backend` | Start FastAPI server on :8000 with auto-reload |
| `make dev-frontend` | Start Vite + React on :5173 with hot reload |
| `make dev` | Start full stack via Docker Compose |
| `make test` | Run all tests (backend + frontend) |
| `make test-unit` | Backend unit tests only |
| `make lint` | Lint: ruff (Python) + eslint (TypeScript) |
| `make typecheck` | Type check: mypy (Python) + tsc (TypeScript) |
| `make format` | Auto-format: ruff + prettier |
| `make seed` | Re-seed the database (drops existing data) |
| `make build` | Build production Docker images |

---

## Environment Variables

The `.env` file is created automatically by `make bootstrap` from `.env.example`. Key variables:

| Variable | Required | Description | Where to get it |
|----------|----------|-------------|-----------------|
| `SE_OGD_API_KEY` | Yes | data.gov.in API key | [data.gov.in/help/apis](https://data.gov.in/help/apis) |
| `SE_LLM_API_KEY` | No | LLM key for AI agents | [openrouter.ai/keys](https://openrouter.ai/keys) (free) |
| `SE_LLM_PROVIDER` | No | `openrouter` (default), `openai`, or `ollama` | — |
| `SE_DATABASE_URL` | Auto | PostgreSQL connection string | Set by bootstrap |
| `SE_REDIS_URL` | Auto | Redis connection string | Set by bootstrap |
| `SE_JWT_SECRET_KEY` | Auto | JWT signing secret | Change in production |

See `.env.example` for the full list of available options.

---

## AI Agents

The `/agents` page provides a chat interface to 4 AI-powered agents. They require an LLM API key set in `.env`.

| Agent | What it does |
|-------|-------------|
| **Prospect Agent** | Analyzes company fit for sales targeting, suggests outreach |
| **Deal Intel Agent** | Assesses deal risk, detects warning signals, generates recovery plays |
| **Retention Agent** | Predicts churn probability, recommends intervention strategies |
| **Competitive Agent** | Generates battlecards, tracks competitor moves |

**Supported LLM providers:**

| Provider | Config | Cost |
|----------|--------|------|
| [OpenRouter](https://openrouter.ai/keys) | `SE_LLM_PROVIDER=openrouter` (default) | Free models available |
| OpenAI | `SE_LLM_PROVIDER=openai`, `SE_LLM_BASE_URL=https://api.openai.com/v1` | Paid |
| Ollama (local) | `SE_LLM_PROVIDER=ollama`, `SE_LLM_BASE_URL=http://localhost:11434/v1` | Free (runs locally) |

---

## Architecture

```
Browser → http://localhost:5173
  │
  ├─ React 18 + TypeScript + Tailwind CSS
  │  8 pages, 14 chart components, "Warm Enterprise" design system
  │
  └─ /api/* proxy → http://localhost:8000
                      │
                      ├─ FastAPI + Python 3.12
                      │  22+ endpoints, 4 AI agents, scoring engines
                      │
                      ├─ PostgreSQL 16 (:5432)
                      │  Users, Prospects, Deals, Signals
                      │
                      └─ Redis 7 (:6379)
                         Multi-tier cache
```

**33 data connectors** for: data.gov.in, RBI DBIE, MOSPI, SEBI, MCA, NSE, BSE, Dhan, Zerodha, Upstox, Finnhub, Alpha Vantage, FMP, CoinGecko, and more.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS, Recharts, Radix UI, Zustand |
| **Backend** | Python 3.12, FastAPI, SQLModel, Pydantic v2, httpx, tenacity |
| **Database** | PostgreSQL 16, Redis 7, DuckDB (analytical) |
| **AI/ML** | scikit-learn, XGBoost, SHAP, OpenRouter / OpenAI LLM |
| **Infra** | Docker Compose, nginx, Prometheus, Grafana, GitHub Actions CI |


