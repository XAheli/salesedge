"""Data normalisation utilities for the ingestion pipeline.

Standardises company names, currency amounts, dates, and Indian state
names across heterogeneous data sources.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# ─── Indian State Normalisation ──────────────────────────────────────────────

STATE_ALIASES: dict[str, str] = {
    "andhra pradesh": "AP", "arunachal pradesh": "AR", "assam": "AS",
    "bihar": "BR", "chhattisgarh": "CG", "goa": "GA", "gujarat": "GJ",
    "haryana": "HR", "himachal pradesh": "HP", "jharkhand": "JH",
    "karnataka": "KA", "kerala": "KL", "madhya pradesh": "MP",
    "maharashtra": "MH", "manipur": "MN", "meghalaya": "ML",
    "mizoram": "MZ", "nagaland": "NL", "odisha": "OD", "orissa": "OD",
    "punjab": "PB", "rajasthan": "RJ", "sikkim": "SK", "tamil nadu": "TN",
    "telangana": "TG", "tripura": "TR", "uttar pradesh": "UP",
    "uttarakhand": "UK", "uttaranchal": "UK", "west bengal": "WB",
    "delhi": "DL", "new delhi": "DL", "nct of delhi": "DL",
    "chandigarh": "CH", "puducherry": "PY", "pondicherry": "PY",
    "jammu and kashmir": "JK", "jammu & kashmir": "JK",
    "ladakh": "LA", "lakshadweep": "LD",
    "andaman and nicobar": "AN", "andaman & nicobar": "AN",
    "dadra and nagar haveli and daman and diu": "DD",
    "dadra and nagar haveli": "DD", "daman and diu": "DD",
    "daman & diu": "DD",
}

VALID_STATE_CODES: set[str] = set(STATE_ALIASES.values())

# Company name normalisation patterns
_COMPANY_SUFFIXES = re.compile(
    r"\b(private|pvt|ltd|limited|llp|inc|corp|corporation|co|company|"
    r"enterprises|solutions|technologies|tech|services|india)\b",
    re.IGNORECASE,
)
_WHITESPACE = re.compile(r"\s+")
_NON_ALNUM = re.compile(r"[^a-z0-9\s]")

# Date parsing formats (common in Indian data sources)
DATE_FORMATS: list[str] = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%Y/%m/%d",
    "%d %b %Y",
    "%d %B %Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%d-%b-%Y",
]

# INR unit multipliers
UNIT_MULTIPLIERS: dict[str, float] = {
    "cr": 1e7,
    "crore": 1e7,
    "crores": 1e7,
    "l": 1e5,
    "lac": 1e5,
    "lakh": 1e5,
    "lakhs": 1e5,
    "k": 1e3,
    "thousand": 1e3,
    "thousands": 1e3,
    "m": 1e6,
    "mn": 1e6,
    "million": 1e6,
    "b": 1e9,
    "bn": 1e9,
    "billion": 1e9,
}


class DataNormalizer:
    """Normalise heterogeneous data from Indian sources into a standard form."""

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """Standardise a company name for deduplication and matching.

        Lowercases, strips common suffixes (Pvt, Ltd, LLP, etc.), removes
        special characters, and collapses whitespace.
        """
        if not name:
            return ""
        normalised = name.lower().strip()
        normalised = _COMPANY_SUFFIXES.sub("", normalised)
        normalised = _NON_ALNUM.sub(" ", normalised)
        normalised = _WHITESPACE.sub(" ", normalised).strip()
        return normalised

    @staticmethod
    def normalize_amount_inr(amount: float | str, unit: str = "") -> float:
        """Convert an amount with a unit label to absolute INR.

        Examples:
            normalize_amount_inr(12.5, "Cr") → 125_000_000.0
            normalize_amount_inr("₹50L")     → 5_000_000.0
        """
        if isinstance(amount, str):
            cleaned = re.sub(r"[₹,\s]", "", amount)
            match = re.match(r"^([0-9.]+)\s*(\w*)$", cleaned)
            if not match:
                raise ValueError(f"Cannot parse amount: {amount!r}")
            numeric = float(match.group(1))
            unit = match.group(2) or unit
        else:
            numeric = float(amount)

        multiplier = UNIT_MULTIPLIERS.get(unit.lower().strip(), 1.0)
        return numeric * multiplier

    @staticmethod
    def normalize_date(date_str: str, source_format: str | None = None) -> datetime:
        """Parse a date string into a datetime, trying common Indian formats.

        If ``source_format`` is provided, it is tried first.
        """
        if not date_str:
            raise ValueError("Empty date string")

        date_str = date_str.strip()

        formats = [source_format] + DATE_FORMATS if source_format else DATE_FORMATS
        for fmt in formats:
            if fmt is None:
                continue
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Could not parse date: {date_str!r}")

    @staticmethod
    def normalize_state_name(state: str) -> str:
        """Convert a state name or alias to its standard 2-letter code.

        Returns the original string (uppercased) if already a valid code.
        """
        if not state:
            return ""
        stripped = state.strip()
        upper = stripped.upper()
        if upper in VALID_STATE_CODES:
            return upper

        key = stripped.lower()
        code = STATE_ALIASES.get(key)
        if code:
            return code

        for alias, c in STATE_ALIASES.items():
            if alias in key or key in alias:
                return c

        logger.warning("normalization.unknown_state", state=state)
        return stripped

    def normalize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Apply standard normalisations to a raw ingested record."""
        normalised = dict(record)

        if "company_name" in normalised and normalised["company_name"]:
            normalised["company_name_normalised"] = self.normalize_company_name(
                normalised["company_name"],
            )

        if "state" in normalised and normalised["state"]:
            normalised["state_code"] = self.normalize_state_name(normalised["state"])

        for date_field in ("timestamp", "published_at", "filing_date", "last_updated"):
            if date_field in normalised and isinstance(normalised[date_field], str):
                try:
                    normalised[date_field] = self.normalize_date(normalised[date_field])
                except ValueError:
                    pass

        for amount_field in ("revenue_inr", "deal_value_inr", "funding_amount_inr"):
            val = normalised.get(amount_field)
            unit = normalised.get(f"{amount_field}_unit", "")
            if val is not None:
                try:
                    normalised[amount_field] = self.normalize_amount_inr(val, unit)
                except (ValueError, TypeError):
                    pass

        return normalised
