"""Integration tests for the data ingestion pipeline.

Tests the full flow: connector fetch → deduplication → normalization →
quality scoring → database insert.
"""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestIngestionPipeline:
    async def test_pipeline_processes_ogd_records(self, db_session):
        """Verify the pipeline can ingest OGD records end-to-end."""
        from app.ingestion.pipeline import IngestionPipeline

        mock_records = [
            {
                "source": "ogd_india",
                "title": "Industrial Production Index",
                "org": "MOSPI",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": {"index_value": 132.5, "period": "2024-Q3"},
            },
            {
                "source": "ogd_india",
                "title": "Consumer Price Index",
                "org": "MOSPI",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "data": {"index_value": 189.3, "period": "2024-Q3"},
            },
        ]

        pipeline = IngestionPipeline(session=db_session)

        with patch.object(pipeline, "_fetch_from_connector", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = mock_records
            result = await pipeline.run(source="ogd_india")

        assert result.records_fetched == 2
        assert result.records_stored >= 1
        assert result.errors == 0

    async def test_deduplication_skips_existing_records(self, db_session):
        """Verify duplicate records are detected and skipped."""
        from app.ingestion.deduplication import Deduplicator

        dedup = Deduplicator(session=db_session)
        record = {
            "source": "finnhub",
            "entity_id": "INFY",
            "data_hash": "abc123",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

        is_new_first = await dedup.is_new(record)
        assert is_new_first is True

        await dedup.mark_seen(record)

        is_new_second = await dedup.is_new(record)
        assert is_new_second is False

    async def test_normalization_formats_indian_currency(self):
        """Verify INR formatting follows Indian number conventions."""
        from app.ingestion.normalization import normalize_currency

        assert normalize_currency(1_50_00_000) == "₹1.50 Cr"
        assert normalize_currency(75_000) == "₹75,000"
        assert normalize_currency(10_00_00_00_000) == "₹1,000.00 Cr"

    async def test_quality_scorer_produces_valid_range(self):
        """Verify quality scores are in [0, 1]."""
        from app.ingestion.quality_scorer import QualityScorer

        scorer = QualityScorer()
        record = {
            "source": "nse",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "data": {"symbol": "TCS", "price": 3800.5, "volume": 1_200_000},
        }
        score = scorer.score(record)
        assert 0.0 <= score <= 1.0

    async def test_pipeline_handles_connector_failure_gracefully(self, db_session):
        """Verify pipeline continues when a connector raises an exception."""
        from app.ingestion.pipeline import IngestionPipeline

        pipeline = IngestionPipeline(session=db_session)

        with patch.object(
            pipeline, "_fetch_from_connector", new_callable=AsyncMock
        ) as mock_fetch:
            mock_fetch.side_effect = ConnectionError("API unreachable")
            result = await pipeline.run(source="finnhub")

        assert result.records_fetched == 0
        assert result.errors >= 1
