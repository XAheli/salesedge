from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import factory
from factory import fuzzy

from app.models.signal import Signal

_SOURCES = ["RBI", "SEBI", "MOSPI", "Economic Times", "Livemint",
            "Moneycontrol", "Business Standard", "Government of India"]

_SIGNAL_TYPES = [
    "policy_rate_change", "regulatory_update", "budget_announcement",
    "industry_news", "competitor_funding", "technology_change",
    "economic_indicator", "corporate_action",
]

_TITLES = {
    "policy_rate_change": [
        "RBI holds repo rate at 6.5%",
        "RBI cuts CRR by 50 bps",
        "MPC votes unanimously for status quo",
    ],
    "regulatory_update": [
        "SEBI introduces new AIF framework",
        "RBI tightens digital lending norms",
        "DPDP Act rules notified",
    ],
    "budget_announcement": [
        "Union Budget: Rs 11 lakh crore capex allocation",
        "PLI scheme extended to new sectors",
        "Startup India 2.0 launched with enhanced benefits",
    ],
    "industry_news": [
        "Indian IT sector to grow 8-10% in FY27",
        "Pharma exports cross $30 billion",
        "SaaS unicorns reach 30 in India",
    ],
    "competitor_funding": [
        "Zoho raises strategic round at $20B valuation",
        "Freshworks acquires AI startup for $80M",
        "HubSpot launches India pricing tier",
    ],
    "technology_change": [
        "GenAI adoption in Indian enterprises doubles",
        "UPI transactions cross 20 billion monthly",
        "Google and Microsoft triple India data centre capacity",
    ],
    "economic_indicator": [
        "India GDP grows 7.3% in Q3 FY26",
        "CPI inflation eases to 4.2%",
        "GST collections hit Rs 2.10 lakh crore",
    ],
}


def _summary_for_type(signal_type: str) -> str:
    summaries = {
        "policy_rate_change": "Monetary policy decision impacting lending rates and BFSI sector sentiment.",
        "regulatory_update": "New regulatory framework requiring compliance adjustments across affected sectors.",
        "budget_announcement": "Government fiscal policy announcement with implications for infrastructure and manufacturing investment.",
        "industry_news": "Industry trend report with implications for TAM sizing and sector-level prospecting.",
        "competitor_funding": "Competitive intelligence signal indicating market positioning changes.",
        "technology_change": "Technology adoption trend affecting enterprise buying behaviour and CRM requirements.",
        "economic_indicator": "Macro-economic data point informing overall enterprise spending confidence.",
    }
    return summaries.get(signal_type, "Market signal requiring sales team attention.")


class SignalFactory(factory.Factory):
    """Factory for generating realistic market signal records."""

    class Meta:
        model = Signal

    id = factory.LazyFunction(uuid4)
    source = fuzzy.FuzzyChoice(_SOURCES)
    signal_type = fuzzy.FuzzyChoice(_SIGNAL_TYPES)
    title = factory.LazyAttribute(
        lambda o: random.choice(_TITLES.get(o.signal_type, ["Market update"]))
    )
    summary = factory.LazyAttribute(lambda o: _summary_for_type(o.signal_type))
    impact_score = fuzzy.FuzzyFloat(3.0, 9.5)
    raw_data = factory.LazyAttribute(lambda o: {"signal_type": o.signal_type, "auto_generated": True})
    source_url = factory.LazyAttribute(
        lambda o: f"https://example.com/signals/{o.signal_type}/{random.randint(1000, 9999)}"
    )
    published_at = factory.LazyFunction(
        lambda: datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))
    )
    processed_at = factory.LazyFunction(datetime.utcnow)
    affected_entity_ids = factory.LazyFunction(lambda: [])
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class RBISignalFactory(SignalFactory):
    """Signals specifically from RBI."""

    source = "RBI"
    signal_type = fuzzy.FuzzyChoice(["policy_rate_change", "regulatory_update"])
    impact_score = fuzzy.FuzzyFloat(6.0, 9.5)


class CompetitorSignalFactory(SignalFactory):
    """Competitive intelligence signals."""

    source = fuzzy.FuzzyChoice(["Moneycontrol", "Economic Times", "Business Standard"])
    signal_type = "competitor_funding"
    impact_score = fuzzy.FuzzyFloat(7.0, 9.0)
