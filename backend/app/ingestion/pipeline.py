"""Ingestion pipeline orchestrator.

Coordinates data ingestion from all configured connectors, handling
scheduling, deduplication, normalisation, and quality scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

import structlog

from app.ingestion.deduplication import DeduplicationStore
from app.ingestion.normalization import DataNormalizer
from app.ingestion.quality_scorer import QualityScorer

logger = structlog.get_logger(__name__)

VALIDATION_RULES: dict[str, Any] = {
    "name_not_empty": lambda r: bool(r.get("name") or r.get("company_name") or r.get("title")),
    "positive_values": lambda r: all(
        v >= 0 for k, v in r.items() if isinstance(v, (int, float)) and k != "sentiment"
    ),
}


class DataConnector(Protocol):
    """Protocol that all data connectors must satisfy."""

    name: str
    tier: int  # 1 = government, 2 = market, 3 = enrichment

    async def fetch(self, **kwargs: Any) -> list[dict[str, Any]]:
        ...

    async def health_check(self) -> bool:
        ...


@dataclass
class IngestionResult:
    """Summary of an ingestion run."""

    connector_name: str
    records_fetched: int = 0
    records_new: int = 0
    records_duplicate: int = 0
    records_failed: int = 0
    avg_quality_score: float = 0.0
    duration_ms: float = 0.0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)


@dataclass
class PipelineRunSummary:
    """Summary of a full pipeline run across all connectors."""

    run_id: str
    mode: str  # "full" or "incremental"
    connector_results: list[IngestionResult]
    total_new_records: int = 0
    total_duplicates: int = 0
    total_errors: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


class IngestPipeline:
    """Orchestrates data ingestion across all connectors.

    Handles the full ingest lifecycle: fetch → deduplicate → normalise →
    quality-score → persist.
    """

    def __init__(
        self,
        dedup: DeduplicationStore | None = None,
        normalizer: DataNormalizer | None = None,
        quality_scorer: QualityScorer | None = None,
    ) -> None:
        self._connectors: dict[str, DataConnector] = {}
        self._dedup = dedup or DeduplicationStore()
        self._normalizer = normalizer or DataNormalizer()
        self._quality = quality_scorer or QualityScorer()
        self._run_count = 0

    def register_connector(self, connector: DataConnector) -> None:
        self._connectors[connector.name] = connector
        logger.info("pipeline.connector_registered", connector=connector.name)

    def unregister_connector(self, name: str) -> None:
        self._connectors.pop(name, None)

    async def run_full_ingestion(self) -> PipelineRunSummary:
        """Run all connectors in a full ingestion sweep."""
        self._run_count += 1
        run_id = f"full_{self._run_count}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        start = datetime.utcnow()

        logger.info("pipeline.full_run_start", run_id=run_id, connectors=len(self._connectors))

        results: list[IngestionResult] = []
        for name, connector in self._connectors.items():
            result = await self.run_connector(name)
            results.append(result)

        summary = PipelineRunSummary(
            run_id=run_id,
            mode="full",
            connector_results=results,
            total_new_records=sum(r.records_new for r in results),
            total_duplicates=sum(r.records_duplicate for r in results),
            total_errors=sum(r.records_failed for r in results),
            started_at=start,
            completed_at=datetime.utcnow(),
        )

        logger.info(
            "pipeline.full_run_complete",
            run_id=run_id,
            new=summary.total_new_records,
            dupes=summary.total_duplicates,
            errors=summary.total_errors,
        )
        return summary

    async def run_incremental(
        self,
        since: datetime | None = None,
    ) -> PipelineRunSummary:
        """Run all connectors in incremental mode, fetching only new data."""
        self._run_count += 1
        run_id = f"incr_{self._run_count}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        start = datetime.utcnow()

        logger.info("pipeline.incremental_start", run_id=run_id)

        results: list[IngestionResult] = []
        for name in self._connectors:
            result = await self.run_connector(name, since=since)
            results.append(result)

        return PipelineRunSummary(
            run_id=run_id,
            mode="incremental",
            connector_results=results,
            total_new_records=sum(r.records_new for r in results),
            total_duplicates=sum(r.records_duplicate for r in results),
            total_errors=sum(r.records_failed for r in results),
            started_at=start,
            completed_at=datetime.utcnow(),
        )

    async def run_connector(
        self,
        connector_name: str,
        since: datetime | None = None,
    ) -> IngestionResult:
        """Run a single connector through the full ingest pipeline."""
        connector = self._connectors.get(connector_name)
        if not connector:
            return IngestionResult(
                connector_name=connector_name,
                errors=[f"Connector '{connector_name}' not registered"],
            )

        start = datetime.utcnow()
        result = IngestionResult(connector_name=connector_name, started_at=start)

        try:
            healthy = await connector.health_check()
            if not healthy:
                result.errors.append(f"Connector '{connector_name}' health check failed")
                result.duration_ms = self._elapsed_ms(start)
                return result

            kwargs: dict[str, Any] = {}
            if since:
                kwargs["since"] = since

            raw_records = await connector.fetch(**kwargs)
            result.records_fetched = len(raw_records)

            processed_records: list[dict[str, Any]] = []
            quality_scores: list[float] = []
            for record in raw_records:
                content_hash = self._dedup.compute_content_hash(record)
                if self._dedup.is_duplicate(content_hash):
                    result.records_duplicate += 1
                    continue

                try:
                    normalised = self._normalizer.normalize_record(record)
                    q_score = self._quality.overall_quality_score(
                        self._quality.score_completeness(normalised, self._required_fields(connector)),
                        self._quality.score_freshness(
                            normalised.get("last_updated"),
                            self._expected_frequency(connector),
                        ),
                        self._quality.score_accuracy(normalised, VALIDATION_RULES),
                    )
                    quality_scores.append(q_score)
                    self._dedup.mark_ingested(content_hash)
                    processed_records.append(normalised)
                    result.records_new += 1
                except Exception as exc:
                    result.records_failed += 1
                    result.errors.append(f"Record processing error: {exc}")

            if processed_records:
                await self._persist_records(connector_name, processed_records)

            if quality_scores:
                result.avg_quality_score = round(
                    sum(quality_scores) / len(quality_scores), 4,
                )

        except Exception as exc:
            result.errors.append(f"Connector execution error: {exc}")
            logger.error(
                "pipeline.connector_error",
                connector=connector_name,
                error=str(exc),
            )

        result.duration_ms = self._elapsed_ms(start)
        result.completed_at = datetime.utcnow()
        return result

    # ── Helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _required_fields(connector: DataConnector) -> list[str]:
        tier_fields: dict[int, list[str]] = {
            1: ["company_name", "source", "timestamp"],
            2: ["symbol", "exchange", "timestamp"],
            3: ["entity_id", "source", "timestamp"],
        }
        return tier_fields.get(connector.tier, ["source", "timestamp"])

    @staticmethod
    def _expected_frequency(connector: DataConnector) -> float:
        """Expected update frequency in hours."""
        tier_hours: dict[int, float] = {
            1: 24.0,     # government: daily
            2: 0.25,     # market: every 15 min
            3: 1.0,      # enrichment: hourly
        }
        return tier_hours.get(connector.tier, 24.0)

    @staticmethod
    def _elapsed_ms(start: datetime) -> float:
        return (datetime.utcnow() - start).total_seconds() * 1000

    @staticmethod
    async def _persist_records(
        connector_name: str, records: list[dict[str, Any]]
    ) -> None:
        """Store processed records for downstream consumption.

        Currently logs the batch for observability.  Replace with a real
        database write (e.g. INSERT INTO ingested_data) when the storage
        layer is wired up.
        """
        logger.info(
            "pipeline.persist_records",
            connector=connector_name,
            count=len(records),
        )
