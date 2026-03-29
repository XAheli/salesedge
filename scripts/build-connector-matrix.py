#!/usr/bin/env python3
"""Build the connector matrix JSON from the live connector registry.

Scans all connector modules under backend/app/connectors/ and produces
a structured JSON file documenting each connector's capabilities, status,
and configuration requirements.

Usage:
    python scripts/build-connector-matrix.py
    python scripts/build-connector-matrix.py --output data/schemas/connector_matrix.json
"""

from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
CONNECTORS_DIR = BACKEND_DIR / "app" / "connectors"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "schemas" / "connector_matrix.json"

sys.path.insert(0, str(BACKEND_DIR))

CONNECTOR_CATEGORIES = {
    "government": {
        "description": "Indian government open data sources",
        "modules": ["ogd_india", "rbi_dbie", "mospi", "sebi", "mca"],
    },
    "market": {
        "description": "Indian stock exchange APIs",
        "modules": ["nse", "bse"],
    },
    "broker": {
        "description": "Indian stockbroker trading APIs",
        "modules": ["zerodha", "dhan", "upstox", "angelone", "fyers", "icici_breeze"],
    },
    "enrichment": {
        "description": "Global financial data enrichment",
        "modules": ["finnhub", "alpha_vantage", "fmp", "coingecko"],
    },
    "enrichment.fx": {
        "description": "Foreign exchange rate providers",
        "modules": ["exchangerate_host", "open_exchange"],
    },
    "crypto": {
        "description": "Cryptocurrency data sources",
        "modules": ["binance"],
    },
    "communication": {
        "description": "News and communication feeds",
        "modules": ["rss_business"],
    },
    "crm": {
        "description": "CRM integrations",
        "modules": ["simulated_crm"],
    },
}


def discover_connectors() -> list[dict]:
    """Walk the connectors directory and build a matrix entry for each."""
    matrix = []

    for category, info in CONNECTOR_CATEGORIES.items():
        module_path = f"app.connectors.{category}"

        for module_name in info["modules"]:
            full_path = f"{module_path}.{module_name}"
            entry = {
                "name": module_name,
                "category": category.split(".")[0],
                "subcategory": category if "." in category else None,
                "module": full_path,
                "description": info["description"],
                "status": "unknown",
                "requires_api_key": False,
                "rate_limit": None,
                "cache_ttl_seconds": None,
            }

            try:
                mod = importlib.import_module(full_path)
                connector_cls = getattr(mod, "connector_class", None) or getattr(
                    mod, next((n for n in dir(mod) if n.endswith("Connector")), ""), None
                )
                if connector_cls:
                    entry["status"] = "implemented"
                    if hasattr(connector_cls, "REQUIRES_API_KEY"):
                        entry["requires_api_key"] = connector_cls.REQUIRES_API_KEY
                    if hasattr(connector_cls, "RATE_LIMIT"):
                        entry["rate_limit"] = connector_cls.RATE_LIMIT
                    if hasattr(connector_cls, "CACHE_TTL"):
                        entry["cache_ttl_seconds"] = connector_cls.CACHE_TTL
                else:
                    entry["status"] = "implemented"
            except ImportError:
                entry["status"] = "not_found"
            except Exception as exc:
                entry["status"] = f"error: {exc}"

            matrix.append(entry)

    return matrix


def main():
    parser = argparse.ArgumentParser(description="Build the SalesEdge connector matrix")
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    print(f"Scanning connectors in {CONNECTORS_DIR}...")
    matrix = discover_connectors()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(
            {
                "version": "1.0.0",
                "generated_by": "scripts/build-connector-matrix.py",
                "total_connectors": len(matrix),
                "connectors": matrix,
            },
            f,
            indent=2,
        )

    print(f"Wrote {len(matrix)} connectors to {args.output}")

    by_status = {}
    for c in matrix:
        by_status.setdefault(c["status"], []).append(c["name"])
    for status, names in sorted(by_status.items()):
        print(f"  {status}: {len(names)} ({', '.join(names[:5])}{'...' if len(names) > 5 else ''})")


if __name__ == "__main__":
    main()
