#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source env vars
set -a
source "${ROOT}/.env" 2>/dev/null || true
set +a

# Activate venv and run seed
source "${ROOT}/backend/.venv/bin/activate" 2>/dev/null || true
cd "${ROOT}/backend"
python -m app.fetch_real_data || echo "app.fetch_real_data not found — add backend/app/fetch_real_data.py with seed logic."
