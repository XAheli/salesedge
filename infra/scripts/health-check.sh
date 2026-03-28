#!/usr/bin/env bash
# Post-deploy checks: API, readiness, data-source health (requires running stack).
set -euo pipefail

BASE_URL="${SALESEDGE_HEALTH_BASE_URL:-http://localhost:8000}"
BASE_URL="${BASE_URL%/}"

check_http() {
  local path=$1
  local name=$2
  local code
  code=$(curl -sS -o /tmp/se-health-body.json -w "%{http_code}" "${BASE_URL}${path}") || true
  if [[ "$code" != "200" ]]; then
    echo "FAIL: $name -> HTTP $code (${BASE_URL}${path})"
    cat /tmp/se-health-body.json 2>/dev/null || true
    return 1
  fi
  echo "OK:  $name"
}

echo ">>> Health checks against $BASE_URL"
check_http "/api/v1/health" "liveness"
check_http "/api/v1/health/ready" "readiness"
check_http "/api/v1/health/data-sources" "data sources"

echo ">>> All checks passed"
