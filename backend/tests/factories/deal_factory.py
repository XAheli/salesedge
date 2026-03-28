from __future__ import annotations

import random
from datetime import datetime, timedelta
from uuid import uuid4

import factory
from factory import fuzzy

from app.models.deal import Deal

_OWNERS = ["Rahul Sharma", "Meera Krishnan", "Arjun Desai", "Kavitha Nair", "Priya Singh"]

_TITLES = [
    "SalesEdge Enterprise License",
    "CRM Migration & Integration",
    "AI-Powered Lead Scoring Module",
    "SalesEdge Growth Plan - Annual",
    "Enterprise Analytics Dashboard",
    "Sales Intelligence Platform",
    "Channel Sales CRM",
    "SalesEdge Startup Plan",
    "B2B Sales Suite",
    "Pipeline Management Module",
]

_STAGES = ["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]

_STAGE_DEFAULTS = {
    "Lead": {"days_range": (1, 10), "risk_range": (0.4, 0.7), "win_prob": (0.05, 0.15)},
    "MQL": {"days_range": (1, 14), "risk_range": (0.25, 0.5), "win_prob": (0.15, 0.30)},
    "SQL": {"days_range": (1, 14), "risk_range": (0.2, 0.45), "win_prob": (0.25, 0.45)},
    "Discovery": {"days_range": (3, 21), "risk_range": (0.2, 0.5), "win_prob": (0.30, 0.50)},
    "Proposal": {"days_range": (5, 21), "risk_range": (0.2, 0.55), "win_prob": (0.40, 0.65)},
    "Negotiation": {"days_range": (5, 30), "risk_range": (0.1, 0.4), "win_prob": (0.55, 0.85)},
    "Won": {"days_range": (0, 0), "risk_range": (0.0, 0.0), "win_prob": (1.0, 1.0)},
    "Lost": {"days_range": (0, 0), "risk_range": (0.7, 1.0), "win_prob": (0.0, 0.0)},
}


class DealFactory(factory.Factory):
    """Factory for generating realistic deal records with stage-aware defaults."""

    class Meta:
        model = Deal

    id = factory.LazyFunction(uuid4)
    prospect_id = factory.LazyFunction(uuid4)
    title = fuzzy.FuzzyChoice(_TITLES)
    stage = fuzzy.FuzzyChoice(["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation"])
    value_inr = fuzzy.FuzzyFloat(1e5, 5e8)
    expected_close_date = factory.LazyFunction(
        lambda: datetime.utcnow() + timedelta(days=random.randint(30, 180))
    )
    owner = fuzzy.FuzzyChoice(_OWNERS)
    risk_score = factory.LazyAttribute(
        lambda o: round(
            random.uniform(*_STAGE_DEFAULTS[o.stage]["risk_range"]) * 100, 2
        )
    )
    risk_score_confidence = fuzzy.FuzzyFloat(0.3, 1.0)
    days_in_stage = factory.LazyAttribute(
        lambda o: random.randint(*_STAGE_DEFAULTS[o.stage]["days_range"])
    )
    engagement_score = fuzzy.FuzzyFloat(10.0, 95.0)
    competitor_mentions = fuzzy.FuzzyInteger(0, 5)
    win_probability = factory.LazyAttribute(
        lambda o: round(
            random.uniform(*_STAGE_DEFAULTS[o.stage]["win_prob"]), 2
        )
    )
    actual_outcome = None
    closed_at = None
    loss_reason = None
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class WonDealFactory(DealFactory):
    """Factory for deals that have been won."""

    stage = "Won"
    actual_outcome = "won"
    win_probability = 1.0
    risk_score = 0.0
    days_in_stage = 0
    closed_at = factory.LazyFunction(
        lambda: datetime.utcnow() - timedelta(days=random.randint(1, 90))
    )


class LostDealFactory(DealFactory):
    """Factory for deals that have been lost."""

    stage = "Lost"
    actual_outcome = "lost"
    win_probability = 0.0
    days_in_stage = 0
    loss_reason = fuzzy.FuzzyChoice([
        "Chose incumbent (Salesforce)",
        "Budget constraints",
        "No decision - status quo",
        "Went with competitor (Zoho CRM)",
        "Project deferred to next FY",
        "Price too high",
        "Feature gap - missing industry-specific capability",
    ])
    closed_at = factory.LazyFunction(
        lambda: datetime.utcnow() - timedelta(days=random.randint(1, 90))
    )
