from __future__ import annotations

import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import structlog

from app.connectors.base import BaseConnector, ConnectorHealth, ConnectorTier

logger = structlog.get_logger(__name__)

_INDUSTRIES = [
    "Information Technology",
    "Banking & Financial Services",
    "Manufacturing",
    "Pharmaceuticals",
    "Telecommunications",
    "Energy & Utilities",
    "Retail & FMCG",
    "Automotive",
    "Real Estate & Infrastructure",
    "Healthcare",
    "Education & EdTech",
    "Logistics & Supply Chain",
    "Agriculture & Agritech",
    "Media & Entertainment",
    "Government & PSU",
]

_CITIES = [
    "Mumbai",
    "Delhi NCR",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
    "Jaipur",
    "Lucknow",
    "Chandigarh",
    "Kochi",
    "Indore",
    "Coimbatore",
    "Vadodara",
]

_COMPANY_SUFFIXES = [
    "Industries Ltd",
    "Technologies Pvt Ltd",
    "Solutions Ltd",
    "Enterprises Pvt Ltd",
    "Infra Ltd",
    "Services Ltd",
    "Systems Pvt Ltd",
    "Global Ltd",
    "India Pvt Ltd",
    "Corp Ltd",
]

_FIRST_NAMES = [
    "Aarav",
    "Priya",
    "Rohan",
    "Sneha",
    "Vikram",
    "Ananya",
    "Arjun",
    "Meera",
    "Karthik",
    "Nisha",
    "Rahul",
    "Deepa",
    "Suresh",
    "Lakshmi",
    "Amit",
]

_LAST_NAMES = [
    "Sharma",
    "Patel",
    "Gupta",
    "Reddy",
    "Singh",
    "Kumar",
    "Iyer",
    "Nair",
    "Mehta",
    "Joshi",
    "Agarwal",
    "Verma",
    "Choudhury",
    "Deshmukh",
    "Rao",
]

_DEAL_STAGES = [
    "Prospecting",
    "Qualification",
    "Needs Analysis",
    "Value Proposition",
    "Proposal Sent",
    "Negotiation",
    "Closed Won",
    "Closed Lost",
]

_TITLES = [
    "CTO",
    "VP Engineering",
    "Head of IT",
    "CFO",
    "Director of Procurement",
    "COO",
    "Managing Director",
    "Head of Digital",
    "VP Sales",
    "Chief Data Officer",
]


class SimulatedCRMConnector(BaseConnector):
    """Simulated CRM connector for development and testing.

    Generates realistic Indian B2B company data, contacts, deals, and
    activity timelines without requiring an external CRM service.
    """

    def __init__(
        self,
        seed: int = 42,
        cache_manager: Any | None = None,
    ) -> None:
        super().__init__(
            name="simulated_crm",
            base_url="http://localhost/simulated-crm",
            tier=ConnectorTier.TIER4_CRM,
            cache_manager=cache_manager,
        )
        self._rng = random.Random(seed)
        self._companies: list[dict[str, Any]] = []
        self._contacts: list[dict[str, Any]] = []
        self._deals: list[dict[str, Any]] = []
        self._generated = False

    def _ensure_generated(self, n_companies: int = 50) -> None:
        if self._generated:
            return
        self._companies = [self._gen_company() for _ in range(n_companies)]
        for company in self._companies:
            n_contacts = self._rng.randint(1, 4)
            for _ in range(n_contacts):
                self._contacts.append(self._gen_contact(company["id"], company["name"]))
            n_deals = self._rng.randint(0, 3)
            for _ in range(n_deals):
                self._deals.append(self._gen_deal(company["id"], company["name"]))
        self._generated = True

    # ── Public methods ───────────────────────────────────────────

    async def list_companies(
        self,
        *,
        industry: str | None = None,
        city: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List simulated companies with optional filters."""
        self._ensure_generated()
        results = self._companies
        if industry:
            results = [c for c in results if c["industry"] == industry]
        if city:
            results = [c for c in results if c["city"] == city]
        page = results[offset : offset + limit]
        return {
            "companies": page,
            "total": len(results),
            "limit": limit,
            "offset": offset,
        }

    async def get_company(self, company_id: str) -> dict[str, Any] | None:
        """Retrieve a single company by ID."""
        self._ensure_generated()
        for c in self._companies:
            if c["id"] == company_id:
                return c
        return None

    async def list_contacts(
        self, company_id: str | None = None, *, limit: int = 20, offset: int = 0
    ) -> dict[str, Any]:
        """List contacts, optionally filtered by company."""
        self._ensure_generated()
        results = self._contacts
        if company_id:
            results = [c for c in results if c["company_id"] == company_id]
        page = results[offset : offset + limit]
        return {"contacts": page, "total": len(results)}

    async def list_deals(
        self,
        company_id: str | None = None,
        *,
        stage: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List deals with optional company / stage filter."""
        self._ensure_generated()
        results = self._deals
        if company_id:
            results = [d for d in results if d["company_id"] == company_id]
        if stage:
            results = [d for d in results if d["stage"] == stage]
        page = results[offset : offset + limit]
        return {"deals": page, "total": len(results)}

    async def get_pipeline_summary(self) -> dict[str, Any]:
        """Aggregate pipeline summary by stage."""
        self._ensure_generated()
        summary: dict[str, dict[str, Any]] = {}
        for deal in self._deals:
            s = deal["stage"]
            if s not in summary:
                summary[s] = {"count": 0, "total_value_inr": 0}
            summary[s]["count"] += 1
            summary[s]["total_value_inr"] += deal["value_inr"]
        return {
            "pipeline": summary,
            "total_deals": len(self._deals),
            "total_value_inr": sum(d["value_inr"] for d in self._deals),
        }

    # ── Data generators ──────────────────────────────────────────

    def _gen_company(self) -> dict[str, Any]:
        name_root = self._rng.choice(
            ["Bharat", "Tata", "Reliance", "Infosys", "Wipro", "Mahindra",
             "Adani", "Birla", "Godrej", "Larsen", "Bajaj", "Hinduja",
             "Vedanta", "Aditya", "Kotak", "Jindal", "Hero", "Ashok",
             "Dalmia", "Grasim", "Axis", "Zee", "Sun", "Cipla"]
        )
        suffix = self._rng.choice(_COMPANY_SUFFIXES)
        industry = self._rng.choice(_INDUSTRIES)
        city = self._rng.choice(_CITIES)
        revenue_cr = round(self._rng.uniform(10, 50_000), 2)
        employees = self._rng.choice([50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000])
        return {
            "id": uuid.UUID(int=self._rng.getrandbits(128)).hex,
            "name": f"{name_root} {suffix}",
            "industry": industry,
            "city": city,
            "state": city,
            "country": "India",
            "revenue_inr_cr": revenue_cr,
            "employees": employees,
            "founded_year": self._rng.randint(1950, 2020),
            "website": f"https://www.{name_root.lower()}.co.in",
            "gstin": self._gen_gstin(),
            "created_at": (
                datetime.now(timezone.utc) - timedelta(days=self._rng.randint(30, 730))
            ).isoformat(),
        }

    def _gen_contact(self, company_id: str, company_name: str) -> dict[str, Any]:
        first = self._rng.choice(_FIRST_NAMES)
        last = self._rng.choice(_LAST_NAMES)
        title = self._rng.choice(_TITLES)
        domain = company_name.split()[0].lower()
        return {
            "id": uuid.UUID(int=self._rng.getrandbits(128)).hex,
            "company_id": company_id,
            "first_name": first,
            "last_name": last,
            "title": title,
            "email": f"{first.lower()}.{last.lower()}@{domain}.co.in",
            "phone": f"+91-{self._rng.randint(70000, 99999)}{self._rng.randint(10000, 99999)}",
        }

    def _gen_deal(self, company_id: str, company_name: str) -> dict[str, Any]:
        stage = self._rng.choice(_DEAL_STAGES)
        value = round(self._rng.uniform(5_00_000, 10_00_00_000), 2)
        close_date = datetime.now(timezone.utc) + timedelta(
            days=self._rng.randint(-60, 180)
        )
        return {
            "id": uuid.UUID(int=self._rng.getrandbits(128)).hex,
            "company_id": company_id,
            "company_name": company_name,
            "title": f"{company_name} — {self._rng.choice(['Platform License', 'Annual Subscription', 'Consulting Engagement', 'Implementation'])}",
            "stage": stage,
            "value_inr": value,
            "probability": self._rng.choice([10, 20, 30, 50, 70, 80, 90, 100]),
            "expected_close": close_date.date().isoformat(),
            "owner": f"{self._rng.choice(_FIRST_NAMES)} {self._rng.choice(_LAST_NAMES)}",
        }

    def _gen_gstin(self) -> str:
        state_code = str(self._rng.randint(1, 37)).zfill(2)
        pan_chars = "".join(self._rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        pan_digits = "".join(str(self._rng.randint(0, 9)) for _ in range(4))
        return f"{state_code}{pan_chars}{pan_digits}1Z{self._rng.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"

    # ── Health / metadata ────────────────────────────────────────

    async def health_check(self) -> ConnectorHealth:
        return ConnectorHealth(
            status="healthy",
            last_check=datetime.now(timezone.utc),
            response_time_ms=0.1,
            error_rate=0.0,
            details={"type": "simulated", "companies": len(self._companies)},
        )

    def get_business_use_cases(self) -> list[str]:
        return [
            "prospect_research",
            "deal_intelligence",
            "territory_planning",
            "retention_analysis",
        ]
