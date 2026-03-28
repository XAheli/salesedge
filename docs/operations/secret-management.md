# Secret Management

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Deployment guide](deployment-guide.md)

---

## Environment variable naming (`SE_` prefix)

`app/config.py` uses `pydantic-settings` with `env_prefix="SE_"`. Examples:

| Variable | Purpose |
|----------|---------|
| `SE_DATABASE_URL` | Async Postgres DSN |
| `SE_REDIS_URL` | Redis connection string |
| `SE_OGD_API_KEY` | data.gov.in |
| `SE_JWT_SECRET_KEY` | Signing key for bearer tokens |
| `SE_FINNHUB_API_KEY` | Finnhub token |
| `SE_POLYGON_API_KEY` | Polygon (stub until wired) |

**Rule:** All new secrets MUST use `SE_` + `UPPER_SNAKE_CASE` matching the `Settings` field after prefix stripping.

## Key rotation procedures

1. **Generate** new secret at provider.  
2. **Stage** in secret manager (or staging `.env`).  
3. **Deploy** to one canary API instance; monitor errors.  
4. **Promote** to full fleet.  
5. **Revoke** old credential.  
6. **Audit** access logs for anomalies.

JWT rotation: expect brief user re-login unless you run overlapping valid keys (advanced).

## Secret scoping

| Environment | Storage | Notes |
|-------------|---------|--------|
| **dev** | Local `.env` (gitignored) | Placeholder keys acceptable |
| **staging** | CI/CD secret store | Mirrors prod topology |
| **prod** | KMS / vault + inject at runtime | No secrets in images |

Never commit `.env` files. Use `.env.example` for non-secret defaults only.

---

[← Documentation index](../README.md)
