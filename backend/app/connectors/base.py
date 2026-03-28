from __future__ import annotations

import enum
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = structlog.get_logger(__name__)


class ConnectorTier(str, enum.Enum):
    TIER1_GOVERNMENT = "tier1_government"
    TIER2_EXCHANGE = "tier2_exchange"
    TIER3_ENRICHMENT = "tier3_enrichment"
    TIER4_CRM = "tier4_crm"


@dataclass
class ConnectorHealth:
    status: Literal["healthy", "degraded", "unhealthy"]
    last_check: datetime
    response_time_ms: float
    error_rate: float
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "last_check": self.last_check.isoformat(),
            "response_time_ms": round(self.response_time_ms, 2),
            "error_rate": round(self.error_rate, 4),
            "details": self.details,
        }


class CircuitState(str, enum.Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker pattern for upstream API calls.

    Transitions:
      CLOSED  -> OPEN       after ``failure_threshold`` consecutive failures
      OPEN    -> HALF_OPEN  after ``recovery_timeout`` seconds
      HALF_OPEN -> CLOSED   after ``success_threshold`` consecutive successes
      HALF_OPEN -> OPEN     on any failure
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 3,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0.0
        self._log = structlog.get_logger("circuit_breaker")

    @property
    def state(self) -> CircuitState:
        if (
            self._state == CircuitState.OPEN
            and time.monotonic() - self._last_failure_time >= self.recovery_timeout
        ):
            self._state = CircuitState.HALF_OPEN
            self._success_count = 0
            self._log.info("circuit_half_open", recovery_timeout=self.recovery_timeout)
        return self._state

    def allow_request(self) -> bool:
        return self.state != CircuitState.OPEN

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._log.info("circuit_closed")
        else:
            self._failure_count = 0

    def record_failure(self) -> None:
        self._failure_count += 1
        self._last_failure_time = time.monotonic()
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._log.warning("circuit_reopened_from_half_open")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._log.warning("circuit_opened", failures=self._failure_count)

    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0


class CircuitOpenError(Exception):
    """Raised when the circuit breaker is open and the request is rejected."""


class UpstreamError(Exception):
    """Raised when an upstream API returns an HTTP error response."""

    def __init__(self, status_code: int, detail: str, connector: str) -> None:
        self.status_code = status_code
        self.detail = detail
        self.connector = connector
        super().__init__(f"[{connector}] HTTP {status_code}: {detail}")


class BaseConnector(ABC):
    """Abstract base for all external API connectors.

    Provides:
    - Automatic retry with exponential backoff (tenacity)
    - Circuit breaker to stop hammering failing upstreams
    - Optional two-tier caching via ``CacheManager``
    - Request-level timing metrics and error rate tracking
    - Pluggable auth via ``_apply_auth``
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        tier: ConnectorTier,
        auth_config: dict[str, Any] | None = None,
        rate_limit: int | None = None,
        timeout: float = 30.0,
        cache_manager: Any | None = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.tier = tier
        self.auth_config = auth_config or {}
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.cache = cache_manager

        self._circuit = CircuitBreaker()
        self._client: httpx.AsyncClient | None = None

        self._request_count: int = 0
        self._error_count: int = 0
        self._total_response_time_ms: float = 0.0

        self._log = structlog.get_logger(f"connector.{name}")

    # ── HTTP client lifecycle ────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True,
                http2=False,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    # ── Auth hook ────────────────────────────────────────────────

    def _apply_auth(
        self, headers: dict[str, str], params: dict[str, Any]
    ) -> None:
        """Inject authentication into the outgoing request.  Override in subclasses."""

    # ── Error classification ─────────────────────────────────────

    @staticmethod
    def _classify_error(status_code: int) -> str:
        if status_code == 429:
            return "rate_limited"
        if 400 <= status_code < 500:
            return "client_error"
        if 500 <= status_code < 600:
            return "server_error"
        return "unknown"

    # ── Core request with retry + circuit breaker ────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (httpx.TransportError, httpx.TimeoutException)
        ),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        json: Any | None = None,
        cache_key: str | None = None,
        cache_ttl: int = 300,
    ) -> dict[str, Any]:
        """Execute an HTTP request with retry, circuit breaker, and caching."""
        if not self._circuit.allow_request():
            raise CircuitOpenError(
                f"Circuit breaker open for connector '{self.name}'"
            )

        if cache_key and self.cache:
            cached = await self.cache.get(cache_key)
            if cached is not None:
                self._log.debug("cache_hit", key=cache_key)
                return cached

        req_headers = dict(headers or {})
        req_params = dict(params or {})
        self._apply_auth(req_headers, req_params)

        client = await self._get_client()
        start = time.monotonic()
        try:
            response = await client.request(
                method,
                path,
                params=req_params,
                headers=req_headers,
                json=json,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            self._request_count += 1
            self._total_response_time_ms += elapsed_ms

            if response.status_code >= 400:
                self._error_count += 1
                self._circuit.record_failure()
                self._log.warning(
                    "upstream_error",
                    status=response.status_code,
                    error_class=self._classify_error(response.status_code),
                    elapsed_ms=round(elapsed_ms, 1),
                    path=path,
                )
                raise UpstreamError(
                    response.status_code,
                    response.text[:500],
                    self.name,
                )

            self._circuit.record_success()
            self._log.debug(
                "request_ok",
                status=response.status_code,
                elapsed_ms=round(elapsed_ms, 1),
                path=path,
            )

            data = response.json()
            if cache_key and self.cache:
                await self.cache.set(cache_key, data, cache_ttl)
            return data

        except (httpx.TransportError, httpx.TimeoutException) as exc:
            elapsed_ms = (time.monotonic() - start) * 1000
            self._error_count += 1
            self._circuit.record_failure()
            self._log.error(
                "transport_error",
                error=str(exc),
                elapsed_ms=round(elapsed_ms, 1),
                path=path,
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (httpx.TransportError, httpx.TimeoutException)
        ),
        reraise=True,
    )
    async def _request_raw(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Raw HTTP request returning the full ``httpx.Response``.

        Useful for scraping connectors that need to parse HTML or download CSVs.
        """
        if not self._circuit.allow_request():
            raise CircuitOpenError(
                f"Circuit breaker open for connector '{self.name}'"
            )

        req_headers = dict(headers or {})
        req_params = dict(params or {})
        self._apply_auth(req_headers, req_params)

        client = await self._get_client()
        start = time.monotonic()
        try:
            response = await client.request(
                method, path, params=req_params, headers=req_headers
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            self._request_count += 1
            self._total_response_time_ms += elapsed_ms

            if response.status_code >= 400:
                self._error_count += 1
                self._circuit.record_failure()
            else:
                self._circuit.record_success()

            return response

        except (httpx.TransportError, httpx.TimeoutException) as exc:
            self._error_count += 1
            self._circuit.record_failure()
            self._log.error("transport_error", error=str(exc), path=path)
            raise

    # ── Metrics ──────────────────────────────────────────────────

    @property
    def error_rate(self) -> float:
        if self._request_count == 0:
            return 0.0
        return self._error_count / self._request_count

    @property
    def avg_response_time_ms(self) -> float:
        if self._request_count == 0:
            return 0.0
        return self._total_response_time_ms / self._request_count

    def reset_metrics(self) -> None:
        self._request_count = 0
        self._error_count = 0
        self._total_response_time_ms = 0.0

    # ── Abstract interface ───────────────────────────────────────

    @abstractmethod
    async def health_check(self) -> ConnectorHealth:
        ...

    @abstractmethod
    def get_business_use_cases(self) -> list[str]:
        ...

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} name={self.name!r} "
            f"tier={self.tier.value}>"
        )
