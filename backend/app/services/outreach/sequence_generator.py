"""Outreach sequence generator.

Builds multi-step, multi-channel outreach sequences personalised to the
prospect's fit score, industry, and deal context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class OutreachStep:
    """A single step in an outreach sequence."""

    step_number: int
    channel: str  # email, linkedin, call, whatsapp
    timing_description: str  # e.g. "Day 0", "Day 3"
    delay_days: int
    template_id: str
    subject: str | None = None
    message_preview: str = ""
    personalisation_fields: list[str] = field(default_factory=list)
    fallback_channel: str | None = None


@dataclass
class OutreachSequence:
    """A complete multi-step outreach cadence."""

    prospect_name: str
    fit_score: float
    total_steps: int
    estimated_duration_days: int
    steps: list[OutreachStep]
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


# Sequence templates by tier
HIGH_FIT_SEQUENCE: list[dict[str, Any]] = [
    {"channel": "email", "delay": 0, "template": "high_fit_intro", "subject": "Quick question about {company_name}"},
    {"channel": "linkedin", "delay": 1, "template": "connection_request", "subject": None},
    {"channel": "email", "delay": 3, "template": "value_prop_followup", "subject": "Thought you'd find this relevant, {first_name}"},
    {"channel": "call", "delay": 5, "template": "discovery_call_script", "subject": None},
    {"channel": "email", "delay": 7, "template": "case_study_share", "subject": "How {similar_company} achieved {outcome}"},
    {"channel": "linkedin", "delay": 10, "template": "linkedin_engage", "subject": None},
    {"channel": "email", "delay": 14, "template": "meeting_request", "subject": "15 min to explore {value_prop}?"},
]

MEDIUM_FIT_SEQUENCE: list[dict[str, Any]] = [
    {"channel": "email", "delay": 0, "template": "moderate_fit_intro", "subject": "Idea for {company_name}"},
    {"channel": "email", "delay": 4, "template": "insight_share", "subject": "{industry} trend you should know about"},
    {"channel": "linkedin", "delay": 7, "template": "connection_request", "subject": None},
    {"channel": "email", "delay": 10, "template": "soft_cta_followup", "subject": "Worth a quick chat?"},
    {"channel": "email", "delay": 18, "template": "breakup_email", "subject": "Closing the loop"},
]

LOW_FIT_SEQUENCE: list[dict[str, Any]] = [
    {"channel": "email", "delay": 0, "template": "nurture_intro", "subject": "Resource for {industry} leaders"},
    {"channel": "email", "delay": 14, "template": "content_share", "subject": "{industry} insights from our research"},
    {"channel": "email", "delay": 30, "template": "gentle_check_in", "subject": "Anything changed at {company_name}?"},
]


class OutreachSequenceGenerator:
    """Generate personalised outreach sequences based on prospect data and fit score."""

    def generate_sequence(
        self,
        prospect: dict[str, Any],
        fit_score: float,
        context: dict[str, Any] | None = None,
    ) -> OutreachSequence:
        """Build an outreach cadence tailored to the prospect.

        Parameters
        ----------
        prospect : dict with company_name, industry, state, etc.
        fit_score : 0-100 ICP fit score
        context : optional deal/campaign context
        """
        context = context or {}
        company_name = prospect.get("company_name", "Unknown")

        if fit_score >= 70:
            template = HIGH_FIT_SEQUENCE
            tier = "high"
        elif fit_score >= 40:
            template = MEDIUM_FIT_SEQUENCE
            tier = "medium"
        else:
            template = LOW_FIT_SEQUENCE
            tier = "low"

        steps = self._build_steps(template, prospect, context)

        logger.info(
            "outreach.sequence_generated",
            company=company_name,
            fit_score=fit_score,
            tier=tier,
            steps=len(steps),
        )

        return OutreachSequence(
            prospect_name=company_name,
            fit_score=fit_score,
            total_steps=len(steps),
            estimated_duration_days=steps[-1].delay_days if steps else 0,
            steps=steps,
            metadata={"tier": tier, "context": context},
        )

    def _build_steps(
        self,
        template: list[dict[str, Any]],
        prospect: dict[str, Any],
        context: dict[str, Any],
    ) -> list[OutreachStep]:
        steps: list[OutreachStep] = []

        for idx, t in enumerate(template):
            subject = t.get("subject")
            if subject:
                subject = self._personalise_subject(subject, prospect, context)

            personalisation = self._detect_personalisation_fields(
                t.get("template", ""), prospect,
            )

            steps.append(OutreachStep(
                step_number=idx + 1,
                channel=t["channel"],
                timing_description=f"Day {t['delay']}",
                delay_days=t["delay"],
                template_id=t["template"],
                subject=subject,
                message_preview=self._generate_preview(t["template"], prospect),
                personalisation_fields=personalisation,
                fallback_channel=self._get_fallback(t["channel"]),
            ))

        return steps

    @staticmethod
    def _personalise_subject(
        subject: str,
        prospect: dict[str, Any],
        context: dict[str, Any],
    ) -> str:
        replacements = {
            "{company_name}": prospect.get("company_name", "your company"),
            "{first_name}": prospect.get("contact_first_name", "there"),
            "{industry}": prospect.get("industry", "your industry"),
            "{similar_company}": context.get("similar_company", "a peer company"),
            "{outcome}": context.get("outcome", "significant results"),
            "{value_prop}": context.get("value_prop", "a fit"),
        }
        for placeholder, value in replacements.items():
            subject = subject.replace(placeholder, str(value))
        return subject

    @staticmethod
    def _detect_personalisation_fields(
        template_id: str,
        prospect: dict[str, Any],
    ) -> list[str]:
        fields = ["company_name"]
        if prospect.get("industry"):
            fields.append("industry")
        if prospect.get("state"):
            fields.append("state")
        if prospect.get("revenue_inr"):
            fields.append("revenue_band")
        if prospect.get("contact_first_name"):
            fields.append("contact_name")
        return fields

    @staticmethod
    def _generate_preview(template_id: str, prospect: dict[str, Any]) -> str:
        company = prospect.get("company_name", "the prospect")
        previews: dict[str, str] = {
            "high_fit_intro": f"Personalised introduction highlighting relevance to {company}",
            "moderate_fit_intro": f"Industry-relevant intro for {company}",
            "connection_request": f"LinkedIn connection request with shared context",
            "value_prop_followup": "Follow-up sharing a specific value proposition",
            "discovery_call_script": "Structured discovery call with prepared questions",
            "case_study_share": "Relevant case study from a similar company",
            "meeting_request": "Direct meeting request with clear agenda",
            "insight_share": "Industry insight or trend relevant to the prospect",
            "breakup_email": "Respectful close-the-loop message",
            "nurture_intro": "Light-touch content share for long-term nurture",
        }
        return previews.get(template_id, f"Outreach step for {company}")

    @staticmethod
    def _get_fallback(channel: str) -> str | None:
        fallbacks = {
            "call": "email",
            "linkedin": "email",
            "whatsapp": "email",
        }
        return fallbacks.get(channel)
