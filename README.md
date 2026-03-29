<p align="center">
  <img src="frontend/public/logo.svg" alt="SalesEdge" width="80" height="80" />
</p>

<h1 align="center">SalesEdge</h1>

<p align="center"><strong>Intelligent Sales & Revenue Operations Platform</strong></p>

<p align="center">
  <a href="https://github.com/XAheli/salesedge">GitHub</a> · MIT License
</p>

An India-focused AI platform for enterprise sales teams. Integrates government data (data.gov.in, RBI, MOSPI, SEBI), Indian market data (NSE, BSE), and 25+ financial APIs to power prospect intelligence, deal risk scoring, churn prediction, and competitive analysis.

---

## How to Run Locally

### Prerequisites

Install these **before** running any commands:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-venv python3-pip nodejs npm docker.io docker-compose-v2
sudo systemctl start docker
sudo usermod -aG docker $USER   # then log out and back in

# Verify
python3 --version   # needs 3.10+
node --version      # needs v18+
docker --version    # any recent version
```

For **macOS**: install Python 3.12+ from python.org, Node 20+ from nodejs.org, Docker Desktop from docker.com.

### Step-by-Step Setup


```bash
git clone https://github.com/XAheli/salesedge.git
cd salesedge
```

Then:

```bash
# Step 1: Run bootstrap (first time creates .env and stops)
make bootstrap

# Step 2: Edit .env — add your API key (required)
nano .env
#   Set: SE_OGD_API_KEY=<your key from https://data.gov.in/help/apis>
#   Optional: SE_LLM_API_KEY=<from https://openrouter.ai/keys>

# Step 3: Run bootstrap again (installs everything, starts DB, seeds data)
make bootstrap

# Step 4: Start both backend + frontend in one command
make dev
#   → Backend: http://localhost:8000
#   → Frontend: http://localhost:5173
#   → Press Ctrl+C to stop both

# Step 5: Open http://localhost:5173 in browser
#   → Register → Dashboard
```

> **Note:** `make dev` starts both servers in one terminal. If you prefer separate terminals
> (useful for reading logs), use `make dev-backend` in one terminal and `make dev-frontend` in another.
> Both servers must be running at the same time.

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `make: command not found` | `sudo apt install make` |
| `python3: command not found` | `sudo apt install python3 python3-venv` |
| `node: command not found` | `sudo apt install nodejs npm` |
| `docker: command not found` | `sudo apt install docker.io docker-compose-v2` |
| `permission denied` on docker | `sudo usermod -aG docker $USER` then log out/in |
| `docker compose` not found | Try `docker-compose` or install `docker-compose-v2` |
| Port 5432 already in use | Stop local postgres: `sudo systemctl stop postgresql` |
| Port 8000 already in use | Kill: `lsof -ti:8000 \| xargs kill` |
| Bootstrap fails at alembic | Not a problem — tables auto-create on first API start |
| `npm ERR!` during bootstrap | Delete `frontend/node_modules` and re-run `make bootstrap` |

### What `make bootstrap` Does

1. Creates `.env` from template (first run — then stops for you to add keys)
2. Checks `SE_OGD_API_KEY` is set
3. Creates Python venv + installs backend dependencies
4. Installs frontend npm packages
5. Starts PostgreSQL 16 + Redis 7 via Docker
6. Runs database migrations
7. Seeds 40 real NIFTY companies, deals, and 30 market signals

---

## Commands

| Command | What it does |
|---------|-------------|
| `make bootstrap` | **Run first.** Full setup |
| `make dev` | **Start both** backend + frontend (one command) |
| `make dev-backend` | Start API only on :8000 (needs separate terminal) |
| `make dev-frontend` | Start UI only on :5173 (needs separate terminal) |
| `make test` | Run backend tests |
| `make lint` | Lint Python code |
| `make seed` | Re-seed the database |

---

## Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | Dashboard | KPIs, pipeline funnel, risk heatmap, top deals |
| `/prospects` | Prospects | Searchable table of Indian companies |
| `/deals` | Deals | Pipeline grouped by risk level |
| `/retention` | Retention | Churn analysis and loss reasons |
| `/intelligence` | Intelligence | RBI/SEBI signals, competitor activity |
| `/agents` | AI Agents | Chat with 4 AI agents (needs LLM key) |
| `/data` | Data | API health and data freshness |
| `/settings` | Settings | Profile, API keys, theme |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SE_OGD_API_KEY` | **Yes** | data.gov.in key — [get free](https://data.gov.in/help/apis) |
| `SE_LLM_API_KEY` | No | AI agents key — [OpenRouter](https://openrouter.ai/keys) or [Groq](https://console.groq.com/keys) (both free) |
| `SE_LLM_PROVIDER` | No | `openrouter` (default), `groq`, `openai`, or `ollama` |

---

## AI Agents

4 LLM-powered agents at `/agents`. Set `SE_LLM_API_KEY` in `.env` to enable.

| Provider | Set `SE_LLM_PROVIDER` to | Free? |
|----------|-------------------------|-------|
| [OpenRouter](https://openrouter.ai/keys) | `openrouter` (default) | Yes |
| [Groq](https://console.groq.com/keys) | `groq` | Yes (fast) |
| [OpenAI](https://platform.openai.com/api-keys) | `openai` | No |
| Ollama (local) | `ollama` | Yes (local) |

---

## Architecture

```
Browser → http://localhost:5173
  │
  ├─ React 18 + TypeScript + Tailwind CSS
  │  8 pages, 20 charts, "Warm Enterprise" design
  │
  └─ /api/* → http://localhost:8000
               │
               ├─ FastAPI + Python 3.12
               │  22+ endpoints, 4 AI agents
               │
               ├─ PostgreSQL 16 (:5432)
               └─ Redis 7 (:6379)
```

33 data connectors: data.gov.in, RBI, MOSPI, SEBI, MCA, NSE, BSE, Dhan, Zerodha, Finnhub, and more.

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, TypeScript, Vite 5, Tailwind, Recharts, Radix UI |
| Backend | Python 3.12, FastAPI, SQLModel, Pydantic v2 |
| Database | PostgreSQL 16, Redis 7, DuckDB |
| AI/ML | scikit-learn, SHAP, OpenRouter/Groq/OpenAI LLM |
| Infra | Docker Compose, nginx, Prometheus, GitHub Actions |

---

## Deploy to Production (Free)

See the [deployment section](#deploy-to-production) or use `render.yaml` (Render) + `frontend/vercel.json` (Vercel).

---

## License

MIT · Shuvam Banerji Seal, Aheli Poddar, Alok Mishra
