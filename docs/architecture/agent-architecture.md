# AI Agent Architecture

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Architecture overview](overview.md)

---

## Four specialized agents

| Agent | Module | Focus |
|-------|--------|--------|
| **Prospect** | `app/services/agents/prospect_agent.py` | ICP fit scoring, enrichment triggers, policy/macro context for outbound |
| **Deal Intel** | `app/services/agents/deal_intel_agent.py` | Deal risk score, engagement/stakeholder signals |
| **Retention** | `app/services/agents/retention_agent.py` | Churn hazard, intervention suggestions |
| **Competitive** | `app/services/agents/competitive_agent.py` (`name`: `competitive_intel_agent`) | Competitor mentions, battlecard generation |

All extend `BaseAgent` (`base_agent.py`) and return an `AgentResult` with success flag, narrative summary, structured `metrics`, and optional payloads.

Feature flags in `app/config.py` (`FeatureFlags`) can disable agents during rollout (`enable_retention_agent`, `enable_competitive_agent`, etc.).

## Orchestrator pattern

`AgentOrchestrator` (`orchestrator.py`) maintains a registry of agents by name and provides:

- **`run_all_agents`** — Concurrent execution via `asyncio.gather` with per-agent error isolation.
- **`route_signal`** — Dispatches work based on `signal_type` and records history for observability.

The orchestrator does not embed business rules beyond routing; each agent owns its domain logic.

## Signal routing

`SIGNAL_ROUTING` maps event types to one or more agents:

| Signal type | Target agents (examples) |
|-------------|---------------------------|
| `new_prospect`, `prospect_enrichment` | `prospect_agent` |
| `deal_update`, `engagement_drop`, `stakeholder_change` | `deal_intel_agent` |
| `competitor_mention` | `deal_intel_agent`, `competitive_intel_agent` |
| `churn_signal`, `usage_decline`, `support_escalation` | `retention_agent` |
| `policy_update`, `market_signal` | `prospect_agent`, `deal_intel_agent` |

Adding a new signal type requires updating this map and ensuring the agent implements the expected payload shape.

## Action engine

`ActionEngine` (`action_engine.py`) turns agent outputs into concrete next steps — e.g. CRM tasks, email sequence steps (`app/services/outreach/`), or API callbacks. Design goals:

- **Idempotent actions** where possible (dedupe by `entity_id` + action hash).
- **Priority ordering** aligned with [recovery prioritization](../formulas/handbook.md#94-revenue-recovery-priority).
- **Audit trail** — link actions to `AgentResult.run_id` for compliance.

## Agent lifecycle

```
register_agent(agent)
       │
       ▼
route_signal(...) or run_all_agents(context)
       │
       ├──► AgentContext (run_id, triggered_by, metadata)
       │
       ▼
agent.run(context)  →  AgentResult
       │
       ▼
_record_run / downstream ActionEngine
```

**Lifecycle concerns**

- **Timeouts** — Agents should bound external calls; connectors already use circuit breakers.
- **Retries** — At orchestration level, prefer dead-letter or re-queue over infinite retry.
- **Shutdown** — On app shutdown, cancel pending agent tasks cleanly (FastAPI lifespan hooks).

---

[← Documentation index](../README.md) · [Formula handbook](../formulas/handbook.md)
