from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.base import AuditMixin


class Prospect(AuditMixin, table=True):
    """A prospective customer with enrichment data from Indian public sources."""

    __tablename__ = "prospects"

    company_name: str = Field(index=True, max_length=512)
    industry: str | None = Field(default=None, index=True, max_length=255)
    nic_code: str | None = Field(default=None, max_length=10, description="NIC 2008 code")
    revenue_inr: float | None = Field(default=None, ge=0, description="Annual revenue in INR")
    employee_count: int | None = Field(default=None, ge=0)
    state: str | None = Field(default=None, index=True, max_length=100)
    city: str | None = Field(default=None, max_length=100)
    gst_number: str | None = Field(default=None, max_length=15)
    mca_registration_date: datetime | None = Field(default=None)
    listed_exchange: str | None = Field(
        default=None, max_length=10, description="BSE, NSE, or both"
    )
    bse_code: str | None = Field(default=None, max_length=10)
    nse_symbol: str | None = Field(default=None, max_length=20)
    dpiit_recognized: bool = Field(default=False)
    website: str | None = Field(default=None, max_length=512)
    fit_score: float | None = Field(default=None, ge=0.0, le=100.0)
    fit_score_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    last_enriched_at: datetime | None = Field(default=None)
