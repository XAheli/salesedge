"""Template engine for outreach messages.

Renders parameterised templates for cold outreach, follow-ups, meeting
requests, and proposals with context-aware personalisation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class RenderedMessage:
    """A fully rendered outreach message."""

    template_id: str
    channel: str
    subject: str | None
    body: str
    personalisation_applied: list[str]
    rendered_at: datetime = field(default_factory=datetime.utcnow)


# ─── Built-in Templates ─────────────────────────────────────────────────────

TEMPLATES: dict[str, dict[str, Any]] = {
    "high_fit_intro": {
        "channel": "email",
        "subject": "Quick question about {{company_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I noticed {{company_name}} has been {{growth_signal}} — "
            "impressive momentum in the {{industry}} space.\n\n"
            "We work with companies like {{similar_company}} to "
            "{{value_proposition}}. Given what I see at {{company_name}}, "
            "I think there could be a strong fit.\n\n"
            "Would you be open to a brief 15-minute conversation this week?\n\n"
            "Best,\n{{sender_name}}"
        ),
    },
    "moderate_fit_intro": {
        "channel": "email",
        "subject": "Idea for {{company_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I've been following developments in {{industry}} and thought "
            "{{company_name}} might benefit from {{value_proposition}}.\n\n"
            "We've helped similar organisations in {{state}} achieve "
            "{{outcome}}.\n\n"
            "Happy to share more if you're interested.\n\n"
            "Regards,\n{{sender_name}}"
        ),
    },
    "value_prop_followup": {
        "channel": "email",
        "subject": "Following up — thought you'd find this relevant",
        "body": (
            "Hi {{first_name}},\n\n"
            "Following up on my previous note. I wanted to share a quick "
            "insight: {{insight}}.\n\n"
            "For {{company_name}}, this could mean {{impact}}.\n\n"
            "Worth a quick chat?\n\n"
            "Best,\n{{sender_name}}"
        ),
    },
    "meeting_request": {
        "channel": "email",
        "subject": "15 min to explore how we can help {{company_name}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I'd love to spend 15 minutes walking through how "
            "{{company_name}} could benefit from {{value_proposition}}.\n\n"
            "I have availability {{available_slots}}. Does any of these "
            "work for you?\n\n"
            "If it's easier, here's my calendar link: {{calendar_link}}\n\n"
            "Looking forward,\n{{sender_name}}"
        ),
    },
    "case_study_share": {
        "channel": "email",
        "subject": "How {{similar_company}} achieved {{outcome}}",
        "body": (
            "Hi {{first_name}},\n\n"
            "I thought you'd find this interesting — {{similar_company}}, "
            "a {{industry}} company similar to {{company_name}}, "
            "recently {{outcome}} using our platform.\n\n"
            "Key results:\n{{results_summary}}\n\n"
            "I'd be happy to walk you through the details.\n\n"
            "Best,\n{{sender_name}}"
        ),
    },
    "connection_request": {
        "channel": "linkedin",
        "subject": None,
        "body": (
            "Hi {{first_name}}, I've been following {{company_name}}'s "
            "growth in {{industry}}. Would love to connect and share some "
            "insights that might be relevant to your work."
        ),
    },
    "breakup_email": {
        "channel": "email",
        "subject": "Closing the loop",
        "body": (
            "Hi {{first_name}},\n\n"
            "I've reached out a few times and understand you're busy. "
            "I don't want to keep filling your inbox if the timing isn't right.\n\n"
            "If {{value_proposition}} becomes a priority for "
            "{{company_name}} down the line, I'd be happy to reconnect.\n\n"
            "Wishing you all the best,\n{{sender_name}}"
        ),
    },
    "discovery_call_script": {
        "channel": "call",
        "subject": None,
        "body": (
            "DISCOVERY CALL SCRIPT — {{company_name}}\n"
            "─────────────────────────────\n"
            "Opener: Reference {{growth_signal}} and congratulate.\n"
            "Context questions:\n"
            "  1. What's driving your current priorities in {{industry}}?\n"
            "  2. How are you currently handling {{pain_point}}?\n"
            "  3. Who else is involved in evaluating solutions like this?\n"
            "Value bridge: Connect their answers to {{value_proposition}}.\n"
            "Next step: Propose a deeper session with {{stakeholder_role}}."
        ),
    },
}

# Default values for missing context keys
DEFAULTS: dict[str, str] = {
    "first_name": "there",
    "company_name": "your company",
    "industry": "your industry",
    "state": "India",
    "growth_signal": "growing rapidly",
    "value_proposition": "our platform",
    "similar_company": "a peer organisation",
    "outcome": "significant results",
    "sender_name": "The SalesEdge Team",
    "insight": "a relevant market development",
    "impact": "measurable improvements",
    "results_summary": "• Increased pipeline velocity\n• Improved win rates",
    "available_slots": "this week",
    "calendar_link": "[calendar link]",
    "pain_point": "pipeline management",
    "stakeholder_role": "the broader team",
}

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")


class TemplateEngine:
    """Render outreach templates with context-aware personalisation."""

    def __init__(
        self,
        templates: dict[str, dict[str, Any]] | None = None,
        defaults: dict[str, str] | None = None,
    ) -> None:
        self._templates = templates or TEMPLATES.copy()
        self._defaults = defaults or DEFAULTS.copy()

    def render_template(
        self,
        template_id: str,
        context: dict[str, Any],
    ) -> RenderedMessage:
        """Render a template by ID with the supplied context variables.

        Missing variables fall back to sensible defaults rather than
        leaving raw placeholders in the output.
        """
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Unknown template: {template_id}")

        merged = {**self._defaults, **{k: str(v) for k, v in context.items() if v is not None}}
        applied: list[str] = []

        subject_raw = template.get("subject")
        subject = self._render_string(subject_raw, merged, applied) if subject_raw else None

        body = self._render_string(template["body"], merged, applied)

        return RenderedMessage(
            template_id=template_id,
            channel=template.get("channel", "email"),
            subject=subject,
            body=body,
            personalisation_applied=sorted(set(applied)),
        )

    def list_templates(self) -> list[dict[str, Any]]:
        """Return metadata about all registered templates."""
        result = []
        for tid, t in self._templates.items():
            placeholders = _PLACEHOLDER_RE.findall(t.get("body", ""))
            if t.get("subject"):
                placeholders.extend(_PLACEHOLDER_RE.findall(t["subject"]))
            result.append({
                "template_id": tid,
                "channel": t.get("channel", "email"),
                "required_fields": sorted(set(placeholders)),
                "has_subject": t.get("subject") is not None,
            })
        return result

    def register_template(
        self,
        template_id: str,
        channel: str,
        body: str,
        subject: str | None = None,
    ) -> None:
        """Register a custom template."""
        self._templates[template_id] = {
            "channel": channel,
            "subject": subject,
            "body": body,
        }

    @staticmethod
    def _render_string(
        text: str,
        context: dict[str, str],
        applied: list[str],
    ) -> str:
        def replacer(match: re.Match) -> str:
            key = match.group(1)
            if key in context:
                applied.append(key)
                return context[key]
            return match.group(0)

        return _PLACEHOLDER_RE.sub(replacer, text)
