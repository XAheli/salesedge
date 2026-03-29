from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)


class MOSPIConnector(BaseConnector):
    """MOSPI eSankhyiki connector for national statistical indicators.

    NOTE: eSankhyiki (esankhyiki.mospi.gov.in) does NOT expose a public
    REST API.  Data access requires browser interaction with their
    JavaScript-heavy portal.  The methods below preserve the desired
    interface but return empty results until a headless-browser or
    manual-export pipeline is implemented.
    """

    _BROWSER_REQUIRED_MSG = (
        "eSankhyiki requires browser interaction; "
        "automated REST access is not available"
    )

    def __init__(self, cache_manager: Any | None = None) -> None:
        super().__init__(
            name="mospi",
            base_url="https://esankhyiki.mospi.gov.in",
            tier=ConnectorTier.TIER1_GOVERNMENT,
            cache_manager=cache_manager,
            timeout=40.0,
        )

    # ── Public methods ───────────────────────────────────────────

    async def get_gdp_data(
        self,
        *,
        frequency: str = "quarterly",
        series: str = "current",
    ) -> dict[str, Any]:
        """Fetch GDP data at the given frequency."""
        logger.warning("mospi.get_gdp_data.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "GDP", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def get_cpi_components(
        self, *, base_year: str = "2012"
    ) -> dict[str, Any]:
        """CPI components broken down by group."""
        logger.warning("mospi.get_cpi_components.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "CPI", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def get_iip_data(self) -> dict[str, Any]:
        """Index of Industrial Production."""
        logger.warning("mospi.get_iip_data.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "IIP", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def get_trade_statistics(
        self,
        *,
        trade_type: str | None = None,
    ) -> dict[str, Any]:
        """Merchandise trade statistics (exports/imports)."""
        logger.warning("mospi.get_trade_statistics.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "trade", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def get_employment_data(self) -> dict[str, Any]:
        """Employment and labour-force statistics."""
        logger.warning("mospi.get_employment_data.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "employment", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def get_gsdp_data(
        self, *, state: str | None = None
    ) -> dict[str, Any]:
        """Gross State Domestic Product data."""
        logger.warning("mospi.get_gsdp_data.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "indicator": "GSDP", "data": [], "note": self._BROWSER_REQUIRED_MSG}

    async def search_indicators(self, query: str) -> dict[str, Any]:
        """Free-text search across MOSPI indicators."""
        logger.warning("mospi.search_indicators.unavailable", reason=self._BROWSER_REQUIRED_MSG)
        return {"source": self.name, "query": query, "results": [], "note": self._BROWSER_REQUIRED_MSG}

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="degraded",
            last_check=datetime.now(timezone.utc),
            response_time_ms=0.0,
            error_rate=0.0,
            details={"note": self._BROWSER_REQUIRED_MSG},
        )

    def get_business_use_cases(self) -> list[str]:
        return [
            "macro_context",
            "industry_sizing",
            "territory_planning",
        ]
