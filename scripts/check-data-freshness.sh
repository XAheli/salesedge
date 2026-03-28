#!/usr/bin/env bash
# Call the data-sources health endpoint and exit non-zero on HTTP errors.
set -euo pipefail

BASE_URL="${SALESEDGE_HEALTH_BASE_URL:-http://127.0.0.1:8000}"
BASE_URL="${BASE_URL%/}"
URL="${BASE_URL}/api/v1/health/data-sources"

echo ">>> GET $URL"
curl -fsS "$URL" | python3 -c "import json,sys; json.load(sys.stdin); print('OK')"
