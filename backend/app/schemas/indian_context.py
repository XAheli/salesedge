from __future__ import annotations

from pydantic import BaseModel, Field


class IndianState(BaseModel):
    """Indian state/UT reference data."""

    name: str
    code: str = Field(description="2-letter state code, e.g. 'MH', 'KA', 'DL'")
    zone: str = Field(description="North, South, East, West, Central, Northeast")


class NICCode(BaseModel):
    """National Industrial Classification code reference."""

    code: str = Field(description="NIC 2008 code, e.g. '62011'")
    description: str
    section: str = Field(description="NIC section letter, e.g. 'J' for Information and Communication")
    division: str | None = None
    group: str | None = None


class INRAmount(BaseModel):
    """Indian Rupee amount with formatted display value."""

    value: float = Field(description="Raw numeric value in INR")
    formatted: str = Field(description="Display string, e.g. '₹12.5 Cr'")
    unit: str = Field(description="Cr, L, K, or (none for absolute)")
