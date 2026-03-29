# SalesEdge Makefile

SHELL := /bin/bash

.PHONY: help bootstrap dev dev-backend dev-frontend intranet-proxy-up intranet-proxy-down test test-unit test-integration test-contract test-e2e test-performance test-backtest lint typecheck format build deploy rollback seed generate-types connector-matrix check-freshness

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Development ───
bootstrap:  ## One-command project setup
	bash scripts/bootstrap.sh

dev:  ## Start backend + frontend together (one command)
	@echo "Starting backend on :8000 and frontend on :5173..."
	@echo "Press Ctrl+C to stop both."
	@echo ""
	@set -a; source .env 2>/dev/null || true; set +a; \
	(cd backend && source .venv/bin/activate && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) & \
	(cd frontend && npm run dev -- --host 0.0.0.0 --port 5173) & \
	wait

dev-backend:  ## Start backend only
	cd backend && set -a && source ../.env 2>/dev/null && set +a && source .venv/bin/activate && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:  ## Start frontend only
	cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

intranet-proxy-up:  ## Expose app on intranet HTTP :80 via nginx reverse proxy
	docker rm -f salesedge-intranet-proxy >/dev/null 2>&1 || true
	docker run -d --name salesedge-intranet-proxy --restart unless-stopped -p 80:80 --add-host=host.docker.internal:host-gateway -v $(PWD)/infra/docker/nginx/intranet-dev-host.conf:/etc/nginx/nginx.conf:ro nginx:1.25-alpine

intranet-proxy-down:  ## Stop intranet HTTP proxy container
	docker rm -f salesedge-intranet-proxy >/dev/null 2>&1 || true

# ─── Testing ───
test:  ## Run all tests
	cd backend && source .venv/bin/activate && uv run pytest -v
	cd frontend && npm run test

test-unit:  ## Run unit tests only
	cd backend && source .venv/bin/activate && uv run pytest tests/unit -v

test-integration:  ## Run integration tests
	cd backend && source .venv/bin/activate && uv run pytest tests/integration -v

test-contract:  ## Run contract tests
	cd backend && source .venv/bin/activate && uv run pytest tests/contract -v

test-e2e:  ## Run E2E tests
	cd frontend && npx playwright test

test-performance:  ## Run performance tests
	cd backend && source .venv/bin/activate && uv run locust -f tests/performance/locustfile.py

test-backtest:  ## Run backtesting suite
	cd backend && source .venv/bin/activate && uv run pytest tests/backtesting -v

# ─── Quality ───
lint:  ## Run linters
	cd backend && source .venv/bin/activate && ruff check .
	cd frontend && npm run lint

typecheck:  ## Run type checkers
	cd backend && source .venv/bin/activate && mypy app --strict
	cd frontend && npx tsc --noEmit

format:  ## Format code
	cd backend && source .venv/bin/activate && ruff format .
	cd frontend && npm run format

# ─── Build & Deploy ───
build:  ## Build production containers
	docker-compose -f docker-compose.prod.yml build

deploy:  ## Deploy to production
	bash infra/scripts/deploy.sh

rollback:  ## Rollback last deployment
	bash infra/scripts/rollback.sh

# ─── Data ───
seed:  ## Seed development data
	bash scripts/seed-data.sh

generate-types:  ## Generate TypeScript types from OpenAPI
	bash scripts/generate-types.sh

connector-matrix:  ## Generate connector matrix artifact
	cd backend && source .venv/bin/activate && python scripts/build-connector-matrix.py

check-freshness:  ## Check data source freshness SLAs
	bash scripts/check-data-freshness.sh
