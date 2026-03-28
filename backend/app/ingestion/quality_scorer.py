"""Data quality scoring for ingested records.

Scores each record on three dimensions:
- **Completeness**: fraction of required fields present
- **Freshness**: how recently the data was updated
- **Accuracy**: conformance to validation rules
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any, Callable

import structlog

logger = structlog.get_logger(__name__)


class QualityScorer:
    """Score ingested records on completeness, freshness, and accuracy."""

    @staticmethod
    def score_completeness(
        record: dict[str, Any],
        required_fields: list[str],
    ) -> float:
        """Fraction of required fields that are present and non-empty.

        Returns 1.0 when all required fields are populated.
        """
        if not required_fields:
            return 1.0

        present = 0
        for field_name in required_fields:
            value = record.get(field_name)
            if value is not None and value != "" and value != []:
                present += 1

        return present / len(required_fields)

    @staticmethod
    def score_freshness(
        last_updated: datetime | str | None,
        expected_frequency_hours: float = 24.0,
    ) -> float:
        """Exponential decay score based on data age vs. expected frequency.

        Returns 1.0 when the data was just updated, decaying toward 0 as
        the data ages beyond the expected update frequency.
        """
        if last_updated is None:
            return 0.0

        if isinstance(last_updated, str):
            try:
                last_updated = datetime.fromisoformat(last_updated)
            except ValueError:
                return 0.0

        age_hours = (datetime.utcnow() - last_updated).total_seconds() / 3600.0
        if age_hours <= 0:
            return 1.0

        half_life = expected_frequency_hours
        return math.exp(-0.693 * age_hours / half_life)

    @staticmethod
    def score_accuracy(
        record: dict[str, Any],
        validation_rules: dict[str, Callable[[Any], bool]],
    ) -> float:
        """Fraction of validation rules that the record satisfies.

        Parameters
        ----------
        record : the data record
        validation_rules : mapping of field_name → predicate.
            Each predicate receives the field value and returns True if valid.
        """
        if not validation_rules:
            return 1.0

        passed = 0
        for field_name, rule in validation_rules.items():
            value = record.get(field_name)
            try:
                if rule(value):
                    passed += 1
            except Exception:
                pass

        return passed / len(validation_rules)

    @staticmethod
    def overall_quality_score(
        completeness: float,
        freshness: float,
        accuracy: float,
        weights: tuple[float, float, float] = (0.4, 0.3, 0.3),
    ) -> float:
        """Weighted composite quality score in [0, 1].

        Default weights prioritise completeness (40%), then freshness (30%)
        and accuracy (30%).
        """
        w_c, w_f, w_a = weights
        total_w = w_c + w_f + w_a
        if total_w == 0:
            return 0.0
        return (w_c * completeness + w_f * freshness + w_a * accuracy) / total_w
