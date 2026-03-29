# Migration Plan — WorldMonitor to SalesEdge

## Overview

Step-by-step plan for migrating reusable components from the WorldMonitor reference
repository into SalesEdge while ensuring complete removal of war/conflict modules
and adaptation to the sales domain.

## Phase 1: Foundation (Week 1-2) — COMPLETED

### 1.1 Repository Setup

- [x] Initialize SalesEdge repository with clean git history
- [x] Set up project structure (backend/, frontend/, docs/, infra/)
- [x] Configure pyproject.toml with SalesEdge dependencies
- [x] Configure package.json with React + TypeScript stack
- [x] Set up Docker Compose for local development

### 1.2 Core Infrastructure

- [x] Copy and adapt Dockerfile (backend) — multi-stage Python build
- [x] Copy and adapt Dockerfile (frontend) — multi-stage Node + nginx
- [x] Set up Alembic for database migrations
- [x] Configure CI/CD pipelines (GitHub Actions)
- [x] Set up .env template with SalesEdge-specific variables

### 1.3 Middleware & Utilities

- [x] Adopt request ID middleware (domain-agnostic)
- [x] Adopt rate limiter middleware (domain-agnostic)
- [x] Adopt Indian formatting utilities
- [x] Adopt structured logging setup
- [x] Adopt confidence interval utilities

## Phase 2: Data Layer (Week 3-4) — COMPLETED

### 2.1 Connector Framework

- [x] Adopt BaseConnector abstract class
- [x] Implement government connectors (OGD, RBI, MOSPI, SEBI, MCA)
- [x] Implement market connectors (NSE, BSE)
- [x] Implement broker connectors (Zerodha, Dhan, Upstox, etc.)
- [x] Implement enrichment connectors (Finnhub, Alpha Vantage, FMP, etc.)

### 2.2 Ingestion Pipeline

- [x] Build ingestion pipeline with scheduler
- [x] Add deduplication layer (new — not in WorldMonitor)
- [x] Add normalization layer (adapted for Indian context)
- [x] Add quality scoring layer (new)

### 2.3 Database Models

- [x] Define Prospect model (replaces WorldMonitor's Entity)
- [x] Define Deal model (new)
- [x] Define Signal model (adapted from WorldMonitor's Event)
- [x] Define User model with JWT auth

## Phase 3: Scoring Engines (Week 5-6) — COMPLETED

### 3.1 Build Sales-Specific Scorers

- [x] Prospect Fit Scorer (replaces country risk scorer)
- [x] Deal Risk Scorer (replaces conflict probability)
- [x] Churn Hazard Predictor (replaces crisis detector)
- [x] Recovery Priority Scorer (new)

### 3.2 Calibration Layer

- [x] Implement Platt scaling
- [x] Implement isotonic regression fallback
- [x] Add Brier score monitoring

### 3.3 Feature Store

- [x] Build feature store for prospect features
- [x] Build feature store for deal features
- [x] Build feature store for macro features

## Phase 4: AI Agents (Week 7-8) — COMPLETED

### 4.1 Agent Framework

- [x] Adopt orchestrator pattern (adapted routing logic)
- [x] Build Prospect Agent (replaces geopolitical agent)
- [x] Build Deal Intel Agent (new)
- [x] Build Retention Agent (replaces crisis agent)
- [x] Build Competitive Agent (new)
- [x] Build Action Engine for agent output

### 4.2 LLM Integration

- [x] Adapt LLM client for multiple providers (OpenRouter, OpenAI, Ollama)
- [x] Build prompt templates for each agent persona

## Phase 5: Frontend (Week 9-12) — COMPLETED

### 5.1 Complete Frontend Rebuild

- [x] Design "Warm Enterprise" design system (new — not from WorldMonitor)
- [x] Build Dashboard with KPIs, funnel, heatmap
- [x] Build Prospects page with search, filters, detail drawer
- [x] Build Deals page with risk segments
- [x] Build Retention page with churn analysis
- [x] Build Intelligence page with signal feed
- [x] Build Agents page with chat interface
- [x] Build Data Provenance page
- [x] Build Settings page

## Phase 6: Cleanup & Documentation (Week 13-14) — IN PROGRESS

- [x] Audit for any remaining WorldMonitor references
- [x] Document all removed modules (removal-list.md)
- [x] Document all adopted modules (reusable-modules.md)
- [ ] Complete architecture documentation
- [ ] Complete user guides for all pages
- [ ] Achieve 80% test coverage target
- [ ] Performance testing with Locust
- [ ] Security audit of all API endpoints

## Verification Checklist

- [x] No conflict/war/military code in codebase
- [x] All connectors adapted for Indian market context
- [x] All scoring models use sales-specific features
- [x] All agents have sales personas
- [x] Frontend is 100% new (not ported from WorldMonitor)
- [ ] All documentation complete
- [ ] Test coverage ≥ 80%
