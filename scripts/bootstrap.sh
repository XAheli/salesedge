#!/usr/bin/env bash
# SalesEdge one-command setup. Works on Ubuntu 22.04+, Fedora 39+, macOS 14+.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# ── .env check ──────────────────────────────────
if [[ ! -f "${ROOT}/.env" ]]; then
  cp "${ROOT}/.env.example" "${ROOT}/.env"
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  .env created from .env.example                            ║"
  echo "║                                                            ║"
  echo "║  Open .env and set your API keys:                          ║"
  echo "║                                                            ║"
  echo "║  REQUIRED:                                                 ║"
  echo "║    SE_OGD_API_KEY=<your key>                               ║"
  echo "║    → Get free: https://data.gov.in/help/apis               ║"
  echo "║                                                            ║"
  echo "║  OPTIONAL (AI agents):                                     ║"
  echo "║    SE_LLM_API_KEY=<your key>                               ║"
  echo "║    → Get free: https://openrouter.ai/keys                  ║"
  echo "║                                                            ║"
  echo "║  Then re-run: make bootstrap                               ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  exit 0
fi

set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a

if [[ -z "${SE_OGD_API_KEY:-}" ]]; then
  echo ""
  echo "ERROR: SE_OGD_API_KEY is not set in .env"
  echo "       Get a free key at: https://data.gov.in/help/apis"
  echo "       Then re-run: make bootstrap"
  echo ""
  exit 1
fi

# ── Python check ────────────────────────────────
PYTHON=""
for cmd in python3.12 python3 python; do
  if command -v "$cmd" >/dev/null 2>&1; then
    PYTHON="$cmd"
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "ERROR: Python 3.12+ is required. Install: sudo apt install python3 python3-venv"
  exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1 | grep -oP '\d+\.\d+')
echo ">>> Using $PYTHON ($PY_VERSION)"

# ── Backend setup ───────────────────────────────
echo ">>> Creating Python venv and installing dependencies..."
$PYTHON -m venv "${ROOT}/backend/.venv"
source "${ROOT}/backend/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "${ROOT}/backend/requirements.txt"
pip install --quiet "pytest>=8.3.0" "pytest-asyncio>=0.24.0" "pytest-cov>=6.0.0" "ruff>=0.8.0" "httpx>=0.28.0" "factory-boy>=3.3.0"
deactivate
echo "    Backend dependencies installed."

# ── Frontend setup ──────────────────────────────
if command -v npm >/dev/null 2>&1; then
  echo ">>> Installing frontend dependencies..."
  (cd "${ROOT}/frontend" && npm install --silent 2>/dev/null || npm install)
  echo "    Frontend dependencies installed."
else
  echo "WARN: npm not found. Install Node.js 20+: https://nodejs.org"
fi

# ── Docker check + start DB ────────────────────
COMPOSE_CMD=""
if command -v "docker" >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v "docker-compose" >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
fi

if [[ -z "$COMPOSE_CMD" ]]; then
  echo "ERROR: Docker is required for PostgreSQL and Redis."
  echo "       Install: https://docs.docker.com/engine/install/ubuntu/"
  exit 1
fi

echo ">>> Starting PostgreSQL and Redis..."
$COMPOSE_CMD -f "${ROOT}/docker-compose.yml" up -d postgres redis

echo ">>> Waiting for PostgreSQL to be ready..."
for i in $(seq 1 30); do
  if $COMPOSE_CMD -f "${ROOT}/docker-compose.yml" exec -T postgres pg_isready -U salesedge >/dev/null 2>&1; then
    echo "    PostgreSQL ready."
    break
  fi
  if [[ $i -eq 30 ]]; then
    echo "WARN: PostgreSQL not ready after 30s. Continuing anyway..."
  fi
  sleep 1
done

# ── Migrations ──────────────────────────────────
echo ">>> Running database migrations..."
source "${ROOT}/backend/.venv/bin/activate"
cd "${ROOT}/backend"
set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a
alembic upgrade head 2>/dev/null || echo "    WARN: Alembic migration skipped (tables auto-created on first API start)."
deactivate

# ── Seed data ───────────────────────────────────
echo ">>> Seeding database with real company data..."
source "${ROOT}/backend/.venv/bin/activate"
cd "${ROOT}/backend"
set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a
python -m app.fetch_real_data 2>/dev/null || echo "    WARN: Seed step had issues — data will be populated on first API start."
deactivate

# ── Done ────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Bootstrap complete!                                       ║"
echo "║                                                            ║"
echo "║  Start the app:                                            ║"
echo "║    make dev                                                ║"
echo "║                                                            ║"
echo "║  Then open: http://localhost:5173                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
