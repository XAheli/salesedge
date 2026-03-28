"""Feature store interface.

Provides a unified API for reading, writing, and versioning features
used by scoring engines and ML models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class FeatureStore:
    """Central feature store for entity-level feature vectors.

    The default implementation uses an in-memory dictionary keyed by
    (entity_id, feature_set).  For production, plug in Redis or a
    database-backed store.
    """

    def __init__(self, backend: Any | None = None) -> None:
        self._backend = backend
        self._store: dict[str, dict[str, Any]] = {}
        self._history: dict[str, list[dict[str, Any]]] = {}

    def get_features(
        self,
        entity_id: str,
        feature_set: str,
    ) -> dict[str, Any]:
        """Retrieve the current feature vector for an entity.

        Parameters
        ----------
        entity_id : unique entity identifier (prospect, deal, customer)
        feature_set : name of the feature set (e.g. "prospect_features")

        Returns
        -------
        Feature dictionary; empty dict if not found.
        """
        key = self._make_key(entity_id, feature_set)

        if self._backend is not None:
            return self._get_from_backend(key)

        return dict(self._store.get(key, {}))

    def compute_and_store(
        self,
        entity_id: str,
        feature_set: str,
        features: dict[str, Any] | None = None,
        compute_fn: Any | None = None,
    ) -> dict[str, Any]:
        """Compute features and persist them to the store.

        Either provide pre-computed ``features`` or a ``compute_fn`` that
        will be called to generate them.
        """
        if features is None and compute_fn is not None:
            features = compute_fn(entity_id)
        if features is None:
            features = {}

        features["_computed_at"] = datetime.utcnow().isoformat()
        features["_entity_id"] = entity_id
        features["_feature_set"] = feature_set

        key = self._make_key(entity_id, feature_set)

        if self._backend is not None:
            self._put_to_backend(key, features)
        else:
            self._store[key] = features

        self._append_history(key, features)

        logger.info(
            "feature_store.stored",
            entity_id=entity_id,
            feature_set=feature_set,
            feature_count=len(features) - 3,  # exclude metadata keys
        )
        return features

    def get_historical_features(
        self,
        entity_id: str,
        feature_set: str,
        as_of_date: datetime | None = None,
    ) -> dict[str, Any]:
        """Retrieve a point-in-time feature snapshot.

        Parameters
        ----------
        entity_id : entity identifier
        feature_set : feature set name
        as_of_date : return the latest snapshot before this datetime.
            If None, returns the most recent snapshot.
        """
        key = self._make_key(entity_id, feature_set)
        history = self._history.get(key, [])

        if not history:
            return {}

        if as_of_date is None:
            return dict(history[-1])

        target = as_of_date.isoformat()
        best: dict[str, Any] = {}
        for snapshot in history:
            ts = snapshot.get("_computed_at", "")
            if ts <= target:
                best = snapshot
            else:
                break

        return dict(best)

    def delete_features(self, entity_id: str, feature_set: str) -> bool:
        """Remove features for an entity from the store."""
        key = self._make_key(entity_id, feature_set)
        removed = key in self._store
        self._store.pop(key, None)
        return removed

    def list_feature_sets(self, entity_id: str) -> list[str]:
        """List all feature sets stored for an entity."""
        prefix = f"{entity_id}:"
        return [
            k.split(":", 1)[1]
            for k in self._store
            if k.startswith(prefix)
        ]

    def get_stats(self) -> dict[str, Any]:
        """Return store statistics."""
        return {
            "total_entries": len(self._store),
            "total_history_snapshots": sum(len(v) for v in self._history.values()),
            "unique_entities": len({k.split(":")[0] for k in self._store}),
        }

    # ── Private helpers ──────────────────────────────────────────────────

    @staticmethod
    def _make_key(entity_id: str, feature_set: str) -> str:
        return f"{entity_id}:{feature_set}"

    def _append_history(self, key: str, features: dict[str, Any]) -> None:
        self._history.setdefault(key, []).append(dict(features))

    def _get_from_backend(self, key: str) -> dict[str, Any]:
        """Retrieve from the external backend (Redis, DB, etc.)."""
        try:
            data = self._backend.get(key)
            if data is None:
                return {}
            if isinstance(data, dict):
                return data
            import json
            return json.loads(data)
        except Exception as exc:
            logger.error("feature_store.backend_get_error", error=str(exc))
            return self._store.get(key, {})

    def _put_to_backend(self, key: str, features: dict[str, Any]) -> None:
        """Write to the external backend."""
        try:
            import json
            self._backend.set(key, json.dumps(features, default=str))
        except Exception as exc:
            logger.error("feature_store.backend_put_error", error=str(exc))
            self._store[key] = features
