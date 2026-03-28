# Monitoring Guide

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Runbook](runbook.md)

---

## Prometheus metrics

The backend depends on `prometheus-client`. Recommended exposition:

- Add a `/metrics` route on the FastAPI app (protected in production) scraping:
  - **HTTP:** request count, latency histogram, status codes
  - **Connectors:** `error_rate`, `avg_response_time_ms` exported from registry summary
  - **Cache:** hit/miss counters for L1 and L2
  - **Agents:** run duration, success/failure counts

Example metric names (to implement consistently):

- `salesedge_http_requests_total{method,route,status}`  
- `salesedge_connector_requests_total{connector,tier}`  
- `salesedge_connector_errors_total{connector,error_class}`  
- `salesedge_cache_hits_total{layer}`  
- `salesedge_agent_runs_total{agent,status}`

## Grafana dashboards

Suggested folders:

1. **API SLO** — p50/p95 latency, error budget, QPS  
2. **Connectors** — health map, circuit state, rate-limit events  
3. **Data freshness** — age of last successful ingest per tier  
4. **Business proxy** — scores computed/min (optional)

## Alert rules (starting set)

| Alert | Condition | Severity |
|-------|-----------|----------|
| HighErrorRate | `5xx` > 2% for 5m | critical |
| ConnectorCircuitOpen | any connector circuit OPEN > 10m | warning |
| RedisDown | redis ping fail | critical |
| PostgresConnectionsHigh | pool near max | warning |
| FreshnessSLABreach | tier1 age > 36h | warning |

## Key metrics to watch

- **Golden signals:** latency, traffic, errors, saturation  
- **Queue depth** (if Celery/async workers enabled for ingestion)  
- **JWT validation failures** (auth misconfiguration detector)

---

[← Documentation index](../README.md)
