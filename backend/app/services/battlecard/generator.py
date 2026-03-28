"""Battlecard generator.

Builds structured competitive battlecards with sections for positioning,
objection handling, and pricing comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class BattlecardSection:
    """A named section within a battlecard."""

    heading: str
    content: str
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Battlecard:
    """A complete competitive battlecard."""

    competitor_name: str
    our_product: str
    summary: str
    strengths_theirs: list[str]
    strengths_ours: list[str]
    weaknesses_theirs: list[str]
    positioning: str
    objection_handling: list[dict[str, str]]
    pricing_comparison: str | None
    sections: list[BattlecardSection]
    win_rate: float | None = None
    encounter_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


OUR_DEFAULT_STRENGTHS: list[str] = [
    "India-first data: native MCA, SEBI, RBI, OGD integrations",
    "Real-time government signal processing and regulatory alerts",
    "Multi-agent AI pipeline for autonomous prospect/deal intelligence",
    "Unified view across 28+ Indian data sources",
    "NIC-code-aware industry classification",
    "Built-in compliance awareness (GST, FEMA, RBI directives)",
]


class BattlecardGenerator:
    """Generate and update competitive battlecards."""

    def __init__(
        self,
        our_product_name: str = "SalesEdge",
        our_strengths: list[str] | None = None,
    ) -> None:
        self._our_product = our_product_name
        self._our_strengths = our_strengths or OUR_DEFAULT_STRENGTHS.copy()

    def generate_battlecard(
        self,
        competitor: str,
        our_product: str | None = None,
        deal_context: dict[str, Any] | None = None,
    ) -> Battlecard:
        """Generate a full battlecard for a competitor.

        Parameters
        ----------
        competitor : competitor name or key
        our_product : override our product name
        deal_context : optional context with win/loss data, pricing intel, etc.
        """
        product = our_product or self._our_product
        ctx = deal_context or {}

        strengths_theirs = ctx.get("competitor_strengths", [
            "Established market presence",
            "Broad feature set",
        ])
        weaknesses_theirs = ctx.get("competitor_weaknesses", [
            "Limited India-specific data integrations",
            "No real-time government data pipeline",
            "Generic NLP not trained on Indian business context",
        ])

        positioning = self._build_positioning(competitor, product, ctx)
        objections = self._build_objection_handling(competitor, product, ctx)
        pricing = self._build_pricing_comparison(competitor, ctx)

        sections = [
            BattlecardSection(
                heading="Overview",
                content=self._build_overview(competitor, ctx),
            ),
            BattlecardSection(
                heading="Their Strengths",
                content=self._format_list(strengths_theirs),
            ),
            BattlecardSection(
                heading="Our Strengths",
                content=self._format_list(self._our_strengths),
            ),
            BattlecardSection(
                heading="Their Weaknesses",
                content=self._format_list(weaknesses_theirs),
            ),
            BattlecardSection(
                heading="Positioning",
                content=positioning,
            ),
            BattlecardSection(
                heading="Objection Handling",
                content="\n\n".join(
                    f"**Objection:** {o['objection']}\n**Response:** {o['response']}"
                    for o in objections
                ),
            ),
            BattlecardSection(
                heading="Pricing Comparison",
                content=pricing or "Pricing intelligence pending.",
            ),
        ]

        logger.info(
            "battlecard.generated",
            competitor=competitor,
            sections=len(sections),
        )

        return Battlecard(
            competitor_name=competitor,
            our_product=product,
            summary=f"Competitive battlecard: {product} vs {competitor}",
            strengths_theirs=strengths_theirs,
            strengths_ours=self._our_strengths,
            weaknesses_theirs=weaknesses_theirs,
            positioning=positioning,
            objection_handling=objections,
            pricing_comparison=pricing,
            sections=sections,
            win_rate=ctx.get("win_rate"),
            encounter_count=ctx.get("encounter_count", 0),
        )

    # ── Section builders ─────────────────────────────────────────────────

    @staticmethod
    def _build_overview(competitor: str, ctx: dict[str, Any]) -> str:
        encounters = ctx.get("encounter_count", 0)
        win_rate = ctx.get("win_rate")
        parts = [f"{competitor} is a key competitor in our market."]
        if encounters:
            parts.append(f"Encountered in {encounters} deal(s).")
        if win_rate is not None:
            parts.append(f"Our win rate against them: {win_rate:.0f}%.")
        return " ".join(parts)

    def _build_positioning(
        self, competitor: str, product: str, ctx: dict[str, Any],
    ) -> str:
        return (
            f"Position {product} as the only India-first sales intelligence platform "
            f"with native government data integration. Unlike {competitor}, {product} "
            f"ingests real-time data from MCA, SEBI, RBI, BSE/NSE, and 20+ OGD "
            f"endpoints. Emphasise our multi-agent AI pipeline that autonomously "
            f"monitors deals, predicts churn, and generates recovery plays — "
            f"capabilities that {competitor} does not offer natively."
        )

    @staticmethod
    def _build_objection_handling(
        competitor: str, product: str, ctx: dict[str, Any],
    ) -> list[dict[str, str]]:
        custom = ctx.get("objections", [])
        if custom:
            return custom

        return [
            {
                "objection": f"We already use {competitor}.",
                "response": (
                    f"{product} complements or replaces {competitor} with India-specific "
                    f"data signals that {competitor} simply doesn't have — MCA filings, "
                    f"SEBI disclosures, RBI policy alerts, and NIC-coded industry intelligence."
                ),
            },
            {
                "objection": f"{competitor} has more features.",
                "response": (
                    f"Feature breadth is one thing; signal depth is another. {product} "
                    f"is purpose-built for Indian sales teams — every feature is designed "
                    f"around the Indian regulatory and business landscape."
                ),
            },
            {
                "objection": f"{competitor} is cheaper.",
                "response": (
                    f"Consider the cost of missed signals. {product}'s real-time government "
                    f"data pipeline surfaces opportunities and risks that generic tools miss, "
                    f"directly impacting pipeline velocity and win rates."
                ),
            },
            {
                "objection": "We're not ready to switch platforms.",
                "response": (
                    f"{product} can run alongside your current stack. Start with our "
                    f"signal feed and scoring engine as a complement — most teams see "
                    f"value within the first sprint."
                ),
            },
        ]

    @staticmethod
    def _build_pricing_comparison(
        competitor: str, ctx: dict[str, Any],
    ) -> str | None:
        pricing = ctx.get("pricing_notes")
        if pricing:
            return pricing
        return (
            f"Detailed pricing comparison for {competitor} pending. "
            f"Known: they offer per-seat licensing; we offer usage-based tiers."
        )

    @staticmethod
    def _format_list(items: list[str]) -> str:
        return "\n".join(f"• {item}" for item in items)
