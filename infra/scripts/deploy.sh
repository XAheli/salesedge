#!/usr/bin/env bash
# SalesEdge deploy: pull images, migrate DB, rolling restart, health checks.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
export COMPOSE_FILE

echo ">>> Pulling images"
docker compose -f "$COMPOSE_FILE" pull

echo ">>> Running database migrations (backend service)"
docker compose -f "$COMPOSE_FILE" run --rm backend alembic upgrade head

echo ">>> Rolling restart"
docker compose -f "$COMPOSE_FILE" up -d --no-deps --build backend frontend

echo ">>> Waiting for health"
sleep 5
bash infra/scripts/health-check.sh

echo ">>> Deploy finished"
