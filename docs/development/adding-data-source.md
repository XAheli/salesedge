# Adding a New Data Source Connector

**Product:** SalesEdge — Intelligent Sales & Revenue Operations Platform  

[← Documentation index](../README.md) · [Catalog](../data-sources/catalog.md)

---

## Step-by-step

1. **Choose tier** — `ConnectorTier` enum (`TIER1_GOVERNMENT` … `TIER4_CRM`).  
2. **Create module** — e.g. `app/connectors/enrichment/my_api.py`.  
3. **Subclass `BaseConnector`** — implement `health_check()` and `get_business_use_cases()`.  
4. **Auth** — override `_apply_auth` to inject headers or query params.  
5. **HTTP** — use `_request` for JSON APIs or `_request_raw` for HTML/CSV.  
6. **Cache** — pass `cache_key` / `cache_ttl` to reduce rate-limit pressure.  
7. **Register** — call `registry.register(MyConnector(...))` at module import or wire in app startup (see `ConnectorRegistry`).  
8. **Settings** — add `SE_MY_API_KEY` fields to `Settings` in `app/config.py`.  
9. **Schedule** — if periodic, hook `IngestionScheduler.schedule_connector` with the correct tier.  
10. **Document** — update [catalog](../data-sources/catalog.md) and [connector matrix](../data-sources/connector-matrix.md).

## `BaseConnector` interface (conceptual)

```python
class MyConnector(BaseConnector):
    async def health_check(self) -> ConnectorHealth: ...
    def get_business_use_cases(self) -> list[str]: ...
```

Use cases should align with matrix columns: e.g. `prospecting`, `risk_detection`, `retention`, `competitive_intel`, `macro_context`.

## `ConnectorRegistry`

- Global instance: `app.connectors.registry.registry`.  
- `auto_discover_connectors()` imports subpackages — avoid circular imports.  
- `health_check_all()` for status pages.

## Testing requirements

- **Unit:** Mock `httpx` via patching `_request`; assert auth, paths, cache keys.  
- **Contract:** VCR-style or recorded fixtures for stable responses.  
- **Rate limit:** Test 429 → `UpstreamError` and circuit behavior.  
- **No live keys in CI** — use environment fakes.

Reference tests: `backend/tests/unit/test_connectors/`.

---

[← Documentation index](../README.md)
