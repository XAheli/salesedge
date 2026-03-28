from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EndpointSpec:
    """Specification for a registered API endpoint."""

    method: str
    path: str
    request_model: type | None = None
    response_model: type | None = None
    cache_ttl: int = 0
    auth_required: bool = True
    roles: tuple[str, ...] = field(default_factory=tuple)


ENDPOINT_REGISTRY: dict[str, EndpointSpec] = {
    "health.liveness": EndpointSpec(
        method="GET",
        path="/api/v1/health",
        auth_required=False,
    ),
    "health.readiness": EndpointSpec(
        method="GET",
        path="/api/v1/health/ready",
        auth_required=False,
    ),
    "health.data_sources": EndpointSpec(
        method="GET",
        path="/api/v1/health/data-sources",
        auth_required=False,
    ),
    "dashboard.executive_summary": EndpointSpec(
        method="GET",
        path="/api/v1/dashboard/executive-summary",
        cache_ttl=300,
        roles=("admin", "manager", "analyst"),
    ),
    "prospects.list": EndpointSpec(
        method="GET",
        path="/api/v1/prospects",
        cache_ttl=120,
    ),
    "prospects.detail": EndpointSpec(
        method="GET",
        path="/api/v1/prospects/{prospect_id}",
        cache_ttl=60,
    ),
    "prospects.enrich": EndpointSpec(
        method="POST",
        path="/api/v1/prospects/{prospect_id}/enrich",
        roles=("admin", "manager"),
    ),
    "deals.list": EndpointSpec(
        method="GET",
        path="/api/v1/deals",
        cache_ttl=120,
    ),
    "deals.detail": EndpointSpec(
        method="GET",
        path="/api/v1/deals/{deal_id}",
        cache_ttl=60,
    ),
    "deals.risk_summary": EndpointSpec(
        method="GET",
        path="/api/v1/deals/risk-summary",
        cache_ttl=180,
    ),
    "data_sources.list": EndpointSpec(
        method="GET",
        path="/api/v1/data-sources",
        cache_ttl=60,
        auth_required=False,
    ),
    "data_sources.health": EndpointSpec(
        method="GET",
        path="/api/v1/data-sources/{source_id}/health",
        cache_ttl=30,
        auth_required=False,
    ),
    "retention.customer_health": EndpointSpec(
        method="GET",
        path="/api/v1/retention/customers",
        cache_ttl=120,
        roles=("admin", "manager", "cs"),
    ),
    "retention.churn_predictions": EndpointSpec(
        method="GET",
        path="/api/v1/retention/churn-predictions",
        cache_ttl=300,
        roles=("admin", "manager", "cs"),
    ),
    "competitive.mentions": EndpointSpec(
        method="GET",
        path="/api/v1/competitive/mentions",
        cache_ttl=120,
    ),
    "competitive.battlecard": EndpointSpec(
        method="GET",
        path="/api/v1/competitive/battlecards/{competitor}",
        cache_ttl=600,
    ),
    "signals.feed": EndpointSpec(
        method="GET",
        path="/api/v1/signals",
        cache_ttl=30,
    ),
    "search.global": EndpointSpec(
        method="GET",
        path="/api/v1/search",
        cache_ttl=30,
    ),
    "admin.settings": EndpointSpec(
        method="GET",
        path="/api/v1/admin/settings",
        roles=("admin",),
    ),
}


def get_endpoint(name: str) -> EndpointSpec:
    """Look up an endpoint spec by registry name, raising KeyError if absent."""
    return ENDPOINT_REGISTRY[name]
