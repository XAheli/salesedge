# Backup & Restore

## PostgreSQL

### Automated Backups

Daily backups are scheduled via cron or a Kubernetes CronJob.

```bash
# Backup script (add to crontab: 0 2 * * *)
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
mkdir -p "$BACKUP_DIR"

docker exec salesedge-postgres-1 \
  pg_dump -U salesedge -Fc salesedge \
  > "$BACKUP_DIR/salesedge_${TIMESTAMP}.dump"

# Retain last 7 daily + 4 weekly backups
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete

echo "Backup completed: salesedge_${TIMESTAMP}.dump"
```

### Manual Backup

```bash
# Custom format (recommended — supports selective restore)
docker exec salesedge-postgres-1 \
  pg_dump -U salesedge -Fc salesedge > backup.dump

# Plain SQL (human-readable, larger file)
docker exec salesedge-postgres-1 \
  pg_dump -U salesedge salesedge > backup.sql
```

### Restore

```bash
# From custom format
docker exec -i salesedge-postgres-1 \
  pg_restore -U salesedge -d salesedge --clean --if-exists backup.dump

# From plain SQL
docker exec -i salesedge-postgres-1 \
  psql -U salesedge -d salesedge < backup.sql

# Verify after restore
docker exec salesedge-postgres-1 \
  psql -U salesedge -d salesedge -c "SELECT count(*) FROM prospect;"
```

### Selective Table Restore

```bash
# List contents of a backup
docker exec salesedge-postgres-1 \
  pg_restore -l backup.dump

# Restore only the prospect table
docker exec -i salesedge-postgres-1 \
  pg_restore -U salesedge -d salesedge -t prospect --clean backup.dump
```

## Redis

### Backup

Redis is configured with RDB snapshots. The dump file is at `/data/dump.rdb`
inside the container.

```bash
# Trigger an immediate snapshot
docker exec salesedge-redis-1 redis-cli BGSAVE

# Copy the dump file out
docker cp salesedge-redis-1:/data/dump.rdb ./redis_backup.rdb
```

### Restore

```bash
# 1. Stop Redis
docker compose stop redis

# 2. Replace the dump file
docker cp ./redis_backup.rdb salesedge-redis-1:/data/dump.rdb

# 3. Restart Redis (loads dump on startup)
docker compose start redis

# 4. Verify
docker exec salesedge-redis-1 redis-cli DBSIZE
```

### Cache-Only Strategy

Since Redis in SalesEdge is primarily a cache layer, full restore is often
unnecessary. A simple `FLUSHDB` followed by letting the backend repopulate
caches on demand is the simplest recovery path:

```bash
docker exec salesedge-redis-1 redis-cli FLUSHDB
```

## Backup Verification

Run these checks weekly to ensure backups are restorable:

```bash
# 1. Create a temporary database
docker exec salesedge-postgres-1 \
  createdb -U salesedge salesedge_verify

# 2. Restore into it
docker exec -i salesedge-postgres-1 \
  pg_restore -U salesedge -d salesedge_verify backup.dump

# 3. Run integrity checks
docker exec salesedge-postgres-1 \
  psql -U salesedge -d salesedge_verify \
  -c "SELECT 'prospects', count(*) FROM prospect
      UNION ALL SELECT 'deals', count(*) FROM deal
      UNION ALL SELECT 'signals', count(*) FROM signal;"

# 4. Drop the verification database
docker exec salesedge-postgres-1 \
  dropdb -U salesedge salesedge_verify
```

## Retention Policy

| Type              | Frequency | Retention | Storage          |
|-------------------|-----------|-----------|------------------|
| PostgreSQL daily  | Daily 2AM | 30 days   | Local + S3       |
| PostgreSQL weekly | Sunday    | 12 weeks  | S3               |
| Redis RDB         | Every 5m  | Latest    | Container volume |
