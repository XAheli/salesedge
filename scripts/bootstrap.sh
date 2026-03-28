#!/usr/bin/env bash
# One-command local setup (Section 12.1): toolchains, .env, databases, migrations, seed.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo ">>> Installing uv (if missing)"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

echo ">>> Python venv + dependencies (backend)"
python3 -m venv "${ROOT}/backend/.venv"
# shellcheck source=/dev/null
source "${ROOT}/backend/.venv/bin/activate"
pip install -U pip
pip install -r "${ROOT}/backend/requirements.txt"
pip install "pytest>=8.3.0" "pytest-asyncio>=0.24.0" "pytest-cov>=6.0.0" "mypy>=1.13.0" "ruff>=0.8.0" "httpx>=0.28.0" "factory-boy>=3.3.0"
deactivate

echo ">>> Node dependencies (frontend)"
if command -v npm >/dev/null 2>&1; then
  (cd "${ROOT}/frontend" && (npm ci 2>/dev/null || npm install))
else
  echo "WARN: npm not found; install Node 20 and re-run this script for the frontend."
fi

if [[ ! -f "${ROOT}/.env" ]]; then
  cp "${ROOT}/.env.example" "${ROOT}/.env"
  echo ""
  echo "╔══════════════════════════════════════════════════════════════╗"
  echo "║  .env file created from .env.example                       ║"
  echo "║                                                            ║"
  echo "║  BEFORE CONTINUING, open .env and set your API keys:       ║"
  echo "║                                                            ║"
  echo "║  REQUIRED:                                                 ║"
  echo "║    SE_OGD_API_KEY=<your key>                               ║"
  echo "║    → Get free at: https://data.gov.in/help/apis            ║"
  echo "║                                                            ║"
  echo "║  OPTIONAL (enables AI agents):                             ║"
  echo "║    SE_LLM_API_KEY=<your key>                               ║"
  echo "║    → Get free at: https://openrouter.ai/keys               ║"
  echo "║                                                            ║"
  echo "║  Then re-run: make bootstrap                               ║"
  echo "╚══════════════════════════════════════════════════════════════╝"
  echo ""
  exit 0
fi

# Validate that required keys are set
set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a

if [[ -z "${SE_OGD_API_KEY}" ]]; then
  echo ""
  echo "ERROR: SE_OGD_API_KEY is not set in .env"
  echo "       Get a free API key at: https://data.gov.in/help/apis"
  echo "       Then edit .env and re-run: make bootstrap"
  echo ""
  exit 1
fi

echo ">>> Starting Postgres & Redis (docker compose)"
docker compose -f "${ROOT}/docker-compose.yml" up -d postgres redis

echo ">>> Waiting for Postgres"
for _ in $(seq 1 60); do
  if docker compose -f "${ROOT}/docker-compose.yml" exec -T postgres pg_isready -U salesedge >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ">>> Alembic migrations"
# shellcheck source=/dev/null
source "${ROOT}/backend/.venv/bin/activate"
cd "${ROOT}/backend"
# Source .env so all SE_* vars are available to alembic/pydantic-settings
set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a
alembic upgrade head || echo "WARN: alembic upgrade failed — tables will be auto-created by FastAPI on first run."
deactivate

echo ">>> Seed data"
bash "${ROOT}/scripts/seed-data.sh" || echo "WARN: seed step failed or app.seed_data is not implemented yet."

echo ">>> Bootstrap complete. Start API: make dev-backend   UI: make dev-frontend   Or: docker compose up"
