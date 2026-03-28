# Operational Runbook

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Deployment guide](deployment-guide.md) · [Monitoring](monitoring-guide.md)

---

## Common tasks

### Restart a service

```bash
docker compose -f docker-compose.prod.yml restart backend
docker compose -f docker-compose.prod.yml restart frontend
```

### Rotate API keys

1. Issue new key at provider.  
2. Update secret store / `.env` / CI variables (`SE_*`).  
3. Rolling restart backend workers.  
4. Revoke old key after error rate stabilizes.  
See [secret-management.md](secret-management.md).

### Check data freshness

```bash
make check-freshness
```

Investigate any connector over SLA (see [data-flow](../architecture/data-flow.md) tier schedules).

### Scale read load

- Increase API replicas behind nginx/load balancer.  
- Ensure **single writer** semantics for migrations.  
- Redis must be shared across API instances for cache coherence.

---

## Troubleshooting

| Symptom | Likely cause | Mitigation |
|---------|--------------|------------|
| 429 / rate_limited logs | Upstream quota | Lower schedule frequency; increase TTL; backoff |
| Circuit open errors | Repeated 5xx | Pause jobs; verify provider status; extend `recovery_timeout` temporarily |
| High p95 latency | Cache cold or DB contention | Warm Redis; inspect slow queries; add indexes |
| Stale dashboard | Scheduler stopped or TZ mismatch | Verify `Asia/Kolkata` on scheduler; restart worker |
| Auth 401 spikes | JWT secret rotation drift | Align `SE_JWT_SECRET_KEY` across replicas |

---

## Escalation procedures

| Severity | Definition | Action |
|----------|------------|--------|
| SEV1 | Complete API outage or data corruption | Page on-call; freeze deploys; rollback (`make rollback`) |
| SEV2 | Major feature broken (e.g. scoring unavailable) | War room; enable feature flags to degrade gracefully |
| SEV3 | Single connector degraded | Disable agent routes using that source; communicate ETA |

Document incident timeline, blast radius, and post-incident review within 5 business days for SEV1–2.

---

[← Documentation index](../README.md)
