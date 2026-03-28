#!/usr/bin/env bash
# Fetch OpenAPI from a running backend and regenerate frontend TypeScript types.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENAPI_URL="${OPENAPI_URL:-http://127.0.0.1:8000/openapi.json}"
OUT="${ROOT}/frontend/src/types/api/generated.ts"

mkdir -p "$(dirname "$OUT")"

echo ">>> Fetching ${OPENAPI_URL}"
curl -fsS "$OPENAPI_URL" -o /tmp/salesedge-openapi.json

echo ">>> openapi-typescript -> ${OUT}"
(cd "${ROOT}/frontend" && npx --yes openapi-typescript@7 /tmp/salesedge-openapi.json -o "$OUT")

echo ">>> Done"
