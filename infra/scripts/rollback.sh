#!/usr/bin/env bash
# Roll back to previous image tags and optionally revert DB migrations.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
PREVIOUS_BACKEND_TAG="${PREVIOUS_BACKEND_TAG:-}"
PREVIOUS_FRONTEND_TAG="${PREVIOUS_FRONTEND_TAG:-}"

if [[ -z "$PREVIOUS_BACKEND_TAG" || -z "$PREVIOUS_FRONTEND_TAG" ]]; then
  echo "Set PREVIOUS_BACKEND_TAG and PREVIOUS_FRONTEND_TAG to the last known good GHCR tags (or digests)."
  echo "Example: PREVIOUS_BACKEND_TAG=abc1234 PREVIOUS_FRONTEND_TAG=abc1234 $0"
  exit 1
fi

echo ">>> Rolling back images to backend=$PREVIOUS_BACKEND_TAG frontend=$PREVIOUS_FRONTEND_TAG"
export BACKEND_IMAGE_TAG="$PREVIOUS_BACKEND_TAG"
export FRONTEND_IMAGE_TAG="$PREVIOUS_FRONTEND_TAG"

# docker-compose.prod.yml should substitute these env vars in image: lines; if not, edit compose to match your layout.
docker compose -f "$COMPOSE_FILE" pull
docker compose -f "$COMPOSE_FILE" up -d --no-deps backend frontend

if [[ "${ROLLBACK_DB:-}" == "1" ]]; then
  echo ">>> Alembic downgrade (one revision)"
  docker compose -f "$COMPOSE_FILE" run --rm backend alembic downgrade -1
fi

bash infra/scripts/health-check.sh || true
echo ">>> Rollback complete — verify traffic and logs."
