from __future__ import annotations

import importlib
import pkgutil
from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth

logger = structlog.get_logger(__name__)


class ConnectorRegistry:
    """Central registry that tracks all instantiated connectors.

    Provides discovery, lookup-by-name, bulk health checks, and a factory
    helper for creating connectors with the shared cache manager.
    """

    def __init__(self) -> None:
        self._connectors: dict[str, BaseConnector] = {}

    def register(self, connector: BaseConnector) -> None:
        self._connectors[connector.name] = connector
        logger.info(
            "connector_registered",
            name=connector.name,
            tier=connector.tier.value,
        )

    def unregister(self, name: str) -> None:
        removed = self._connectors.pop(name, None)
        if removed:
            logger.info("connector_unregistered", name=name)

    def get(self, name: str) -> BaseConnector | None:
        return self._connectors.get(name)

    def list_all(self) -> list[BaseConnector]:
        return list(self._connectors.values())

    def list_by_tier(self, tier: str) -> list[BaseConnector]:
        return [c for c in self._connectors.values() if c.tier.value == tier]

    def list_names(self) -> list[str]:
        return list(self._connectors.keys())

    async def health_check_all(self) -> dict[str, ConnectorHealth]:
        results: dict[str, ConnectorHealth] = {}
        for name, connector in self._connectors.items():
            try:
                results[name] = await connector.health_check()
            except Exception as exc:
                logger.warning(
                    "health_check_failed", connector=name, error=str(exc)
                )
                results[name] = ConnectorHealth(
                    status="unhealthy",
                    last_check=datetime.now(timezone.utc),
                    response_time_ms=0.0,
                    error_rate=1.0,
                    details={"error": str(exc)},
                )
        return results

    async def close_all(self) -> None:
        for connector in self._connectors.values():
            try:
                await connector.close()
            except Exception as exc:
                logger.warning(
                    "connector_close_failed",
                    connector=connector.name,
                    error=str(exc),
                )

    def summary(self) -> list[dict[str, Any]]:
        """Return a lightweight summary suitable for API responses."""
        return [
            {
                "name": c.name,
                "tier": c.tier.value,
                "use_cases": c.get_business_use_cases(),
                "error_rate": round(c.error_rate, 4),
                "avg_response_time_ms": round(c.avg_response_time_ms, 2),
            }
            for c in self._connectors.values()
        ]


registry = ConnectorRegistry()


def auto_discover_connectors() -> None:
    """Walk *app.connectors* sub-packages and import every module.

    Each connector module registers itself at import time via the
    module-level ``registry.register(...)`` call, so this function
    does not need to return anything.
    """
    import app.connectors as root_pkg

    for _importer, modname, _ispkg in pkgutil.walk_packages(
        root_pkg.__path__, prefix=root_pkg.__name__ + "."
    ):
        if modname.endswith(("__init__", "base", "registry")):
            continue
        try:
            importlib.import_module(modname)
        except Exception as exc:
            logger.warning(
                "connector_import_failed", module=modname, error=str(exc)
            )
