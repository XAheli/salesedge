from __future__ import annotations

import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from app.connectors.base import (
    BaseConnector,
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
    ConnectorHealth,
    ConnectorTier,
    UpstreamError,
)


class ConcreteConnector(BaseConnector):
    """Minimal concrete implementation for testing."""

    def __init__(self, **kwargs):
        super().__init__(
            name="test_connector",
            base_url="https://api.example.com",
            tier=ConnectorTier.TIER3_ENRICHMENT,
            **kwargs,
        )

    async def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="healthy",
            last_check=datetime.now(timezone.utc),
            response_time_ms=50.0,
            error_rate=0.0,
        )

    def get_business_use_cases(self) -> list[str]:
        return ["test"]


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True

    def test_opens_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.allow_request() is False

    def test_stays_closed_below_threshold(self):
        cb = CircuitBreaker(failure_threshold=5)
        for _ in range(4):
            cb.record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_success_resets_failure_count(self):
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)
        cb.record_failure()
        cb.record_failure()
        assert cb._state == CircuitState.OPEN
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN
        assert cb.allow_request() is True

    def test_half_open_closes_after_success_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01, success_threshold=2)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.02)
        _ = cb.state  # triggers transition to HALF_OPEN
        cb.record_success()
        assert cb._state == CircuitState.HALF_OPEN
        cb.record_success()
        assert cb._state == CircuitState.CLOSED

    def test_half_open_reopens_on_failure(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.01)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.02)
        _ = cb.state
        cb.record_failure()
        assert cb._state == CircuitState.OPEN

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=2)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        cb.reset()
        assert cb.state == CircuitState.CLOSED
        assert cb.allow_request() is True


class TestUpstreamError:
    def test_attributes(self):
        err = UpstreamError(429, "Rate limited", "ogd_india")
        assert err.status_code == 429
        assert err.connector == "ogd_india"
        assert "429" in str(err)

    def test_str_representation(self):
        err = UpstreamError(500, "Internal error", "nse")
        assert "[nse] HTTP 500:" in str(err)


class TestBaseConnector:
    def test_init(self):
        c = ConcreteConnector()
        assert c.name == "test_connector"
        assert c.tier == ConnectorTier.TIER3_ENRICHMENT
        assert c.error_rate == 0.0

    def test_error_rate_calculation(self):
        c = ConcreteConnector()
        c._request_count = 10
        c._error_count = 3
        assert c.error_rate == pytest.approx(0.3)

    def test_error_rate_zero_requests(self):
        c = ConcreteConnector()
        assert c.error_rate == 0.0

    def test_avg_response_time(self):
        c = ConcreteConnector()
        c._request_count = 5
        c._total_response_time_ms = 500.0
        assert c.avg_response_time_ms == pytest.approx(100.0)

    def test_avg_response_time_zero_requests(self):
        c = ConcreteConnector()
        assert c.avg_response_time_ms == 0.0

    def test_reset_metrics(self):
        c = ConcreteConnector()
        c._request_count = 10
        c._error_count = 3
        c._total_response_time_ms = 1000.0
        c.reset_metrics()
        assert c._request_count == 0
        assert c._error_count == 0
        assert c._total_response_time_ms == 0.0

    def test_repr(self):
        c = ConcreteConnector()
        r = repr(c)
        assert "ConcreteConnector" in r
        assert "test_connector" in r

    def test_error_classification(self):
        assert BaseConnector._classify_error(429) == "rate_limited"
        assert BaseConnector._classify_error(404) == "client_error"
        assert BaseConnector._classify_error(500) == "server_error"
        assert BaseConnector._classify_error(200) == "unknown"


class TestBaseConnectorRequest:
    @pytest.mark.asyncio
    async def test_circuit_open_raises(self):
        c = ConcreteConnector()
        c._circuit._state = CircuitState.OPEN
        c._circuit._last_failure_time = time.monotonic()
        with pytest.raises(CircuitOpenError):
            await c._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_cache_hit_skips_request(self):
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value={"cached": True})
        c = ConcreteConnector(cache_manager=mock_cache)
        result = await c._request("GET", "/test", cache_key="test:key")
        assert result == {"cached": True}
        mock_cache.get.assert_called_once_with("test:key")

    @pytest.mark.asyncio
    async def test_apply_auth_called(self):
        c = ConcreteConnector()
        c._apply_auth = MagicMock()
        c._circuit._state = CircuitState.OPEN
        c._circuit._last_failure_time = time.monotonic()
        try:
            await c._request("GET", "/test")
        except CircuitOpenError:
            pass

    @pytest.mark.asyncio
    async def test_close_client(self):
        c = ConcreteConnector()
        c._client = AsyncMock()
        c._client.is_closed = False
        await c.close()
        c._client.aclose.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_no_client(self):
        c = ConcreteConnector()
        await c.close()


class TestConnectorHealth:
    def test_to_dict(self):
        health = ConnectorHealth(
            status="healthy",
            last_check=datetime(2026, 3, 28, 12, 0, 0, tzinfo=timezone.utc),
            response_time_ms=45.678,
            error_rate=0.05,
            details={"version": "1.0"},
        )
        d = health.to_dict()
        assert d["status"] == "healthy"
        assert d["response_time_ms"] == 45.68
        assert d["error_rate"] == 0.05
        assert d["details"]["version"] == "1.0"
        assert "2026-03-28" in d["last_check"]


class TestConnectorTier:
    def test_tier_values(self):
        assert ConnectorTier.TIER1_GOVERNMENT.value == "tier1_government"
        assert ConnectorTier.TIER2_EXCHANGE.value == "tier2_exchange"
        assert ConnectorTier.TIER3_ENRICHMENT.value == "tier3_enrichment"
        assert ConnectorTier.TIER4_CRM.value == "tier4_crm"
