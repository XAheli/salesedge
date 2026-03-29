# Rollback Plan

Procedures for reverting SalesEdge to a known-good state after a failed deployment
or critical regression.

## Decision Matrix

| Severity    | Symptom                                | Action                        |
|-------------|----------------------------------------|-------------------------------|
| **P0**      | API 5xx rate > 10%, data corruption    | Immediate full rollback       |
| **P1**      | Feature broken, scores incorrect        | Targeted service rollback     |
| **P2**      | UI glitch, non-critical bug            | Hotfix forward, no rollback   |

## Docker Compose Rollback

### Full Stack Rollback

```bash
# 1. Stop all services
docker compose down

# 2. Check available image tags
docker images | grep salesedge

# 3. Switch to last known-good tag in docker-compose.yml
#    or set via environment variable
export SALESEDGE_TAG=v1.2.3

# 4. Bring up with pinned images
docker compose up -d

# 5. Verify health
curl -f http://localhost:8000/api/v1/health
curl -f http://localhost:5173
```

### Single Service Rollback

```bash
# Rollback only the backend
docker compose up -d --no-deps --build backend

# Rollback only the frontend
docker compose up -d --no-deps --build frontend
```

## Database Rollback

### Alembic Migration Rollback

```bash
cd backend

# Check current migration head
alembic current

# Downgrade by one revision
alembic downgrade -1

# Downgrade to a specific revision
alembic downgrade abc123def456

# View migration history
alembic history --verbose
```

### PostgreSQL Point-in-Time Recovery

If the migration rollback is insufficient (data corruption), restore from backup:

```bash
# 1. Stop the backend to prevent writes
docker compose stop backend

# 2. Restore from latest backup (see backup-restore.md)
docker exec -i salesedge-postgres-1 \
  pg_restore -U salesedge -d salesedge --clean /backups/latest.dump

# 3. Replay Alembic to the correct migration
cd backend && alembic upgrade head

# 4. Restart backend
docker compose start backend
```

## Redis Rollback

Redis is used as a cache — rollback simply means flushing:

```bash
docker exec salesedge-redis-1 redis-cli FLUSHDB
```

The backend will repopulate caches on the next request cycle.

## Kubernetes Rollback

```bash
# Check rollout history
kubectl rollout history deployment/salesedge-backend -n salesedge

# Rollback to previous revision
kubectl rollout undo deployment/salesedge-backend -n salesedge

# Rollback to specific revision
kubectl rollout undo deployment/salesedge-backend -n salesedge --to-revision=3

# Monitor rollback progress
kubectl rollout status deployment/salesedge-backend -n salesedge
```

## Post-Rollback Checklist

- [ ] Verify `/api/v1/health` returns `200` with all components connected
- [ ] Confirm database migration version matches the deployed code
- [ ] Check Redis connectivity (`redis-cli ping`)
- [ ] Run smoke tests: `make test-unit`
- [ ] Verify dashboard loads with real data at `http://localhost:5173`
- [ ] Notify the team in Slack/Teams with rollback details
- [ ] Create a post-incident ticket documenting root cause
