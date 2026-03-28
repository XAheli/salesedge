"""Prompt templates for SalesEdge AI agents.

Each agent has a system prompt defining its role and behavior,
plus task-specific prompt templates.
"""

SYSTEM_PROMPTS: dict[str, str] = {
    "prospect_agent": (
        "You are a B2B sales intelligence analyst specializing in the Indian market. "
        "You analyze company data from government sources (MCA, GST, DPIIT), "
        "market data (NSE, BSE), and enrichment sources to assess prospect fit. "
        "Always reference Indian business context: INR amounts in lakhs/crores, "
        "Indian financial year (Apr-Mar), NIC industry codes, and state-specific factors. "
        "Be concise, data-driven, and actionable."
    ),
    "deal_intel_agent": (
        "You are a deal risk analyst for B2B enterprise sales in India. "
        "You monitor deal health by analyzing engagement patterns, stakeholder coverage, "
        "stage velocity, sentiment trends, and competitive signals. "
        "When detecting risk, clearly state the risk factor, its severity, "
        "and recommend specific recovery actions. "
        "Reference values in INR (lakhs/crores) and timelines in IST."
    ),
    "retention_agent": (
        "You are a customer success analyst focused on preventing churn "
        "for B2B SaaS customers in India. "
        "You analyze usage patterns, support ticket trends, NPS scores, "
        "and contract renewal proximity to predict churn risk. "
        "Recommend specific interventions ranked by impact and urgency."
    ),
    "competitive_agent": (
        "You are a competitive intelligence analyst for B2B sales. "
        "You track competitor mentions, analyze market signals, "
        "and generate actionable battlecards. "
        "Focus on Indian market dynamics, regulatory changes (SEBI, RBI), "
        "and government policy impacts on enterprise buying."
    ),
}

PROSPECT_ANALYSIS_PROMPT = """\
Analyze this prospect for sales fit:

Company: {company_name}
Industry: {industry}
Revenue: ₹{revenue_cr} Cr
Employees: {employee_count}
State: {state}
Listed: {listed_exchange}
MCA Registration: {mca_date}
GST Status: {gst_status}

Additional data:
{additional_context}

Provide:
1. Fit assessment (score 0-100 with reasoning)
2. Key strengths as a prospect
3. Potential concerns or risks
4. Recommended approach (outreach strategy)
5. Best timing for outreach based on Indian business cycles

Respond in JSON format with keys: fit_assessment, strengths, concerns, approach, timing"""

DEAL_RISK_PROMPT = """\
Analyze this deal for risk:

Deal: {deal_title}
Company: {company_name}
Value: ₹{value_lakhs}L
Stage: {stage}
Days in Stage: {days_in_stage}
Expected Close: {expected_close}

Engagement History:
{engagement_summary}

Stakeholder Coverage:
{stakeholder_summary}

Competitor Mentions: {competitor_mentions}

Provide:
1. Overall risk level (low/medium/high/critical) with score 0-100
2. Top 3 risk factors ranked by severity
3. Specific recovery actions for each risk
4. Recommended next steps
5. Probability of winning this deal

Respond in JSON format with keys: risk_level, risk_score, risk_factors, \
recovery_actions, next_steps, win_probability"""

OUTREACH_GENERATION_PROMPT = """\
Generate a personalized outreach message:

Target Company: {company_name}
Industry: {industry}
Company Size: {company_size}
Key Person: {contact_name} ({contact_title})
Our Product: SalesEdge - Intelligent Sales & Revenue Operations Platform
Fit Score: {fit_score}/100
Key Value Props: {value_props}
Indian Context: {indian_context}

Generate a {channel} message that:
1. Is personalized to their industry and business context
2. References a specific pain point for Indian {industry} companies
3. Is concise (max 150 words for email, 50 for LinkedIn)
4. Has a clear, low-commitment CTA
5. Sounds human, not AI-generated

Respond in JSON: {{subject, body, cta, follow_up_timing}}"""

CHURN_ANALYSIS_PROMPT = """\
Analyze churn risk for this customer:

Customer: {customer_name}
Contract Value: ₹{contract_value_lakhs}L/year
Renewal Date: {renewal_date}
Account Age: {account_age_months} months

Health Signals:
- Usage Trend (30d): {usage_trend}
- Support Tickets (30d): {support_tickets}
- NPS Score: {nps_score}
- Payment History: {payment_status}
- Champion Status: {champion_status}

Market Context:
{market_context}

Provide:
1. Churn probability (0-100) with reasoning
2. Top contributing factors
3. Recommended intervention type (proactive_outreach, offer, escalation, success_review)
4. Specific action plan with timeline
5. Estimated save probability if intervention is executed

Respond in JSON: {{churn_probability, factors, intervention_type, action_plan, \
save_probability}}"""

BATTLECARD_PROMPT = """\
Generate a competitive battlecard:

Competitor: {competitor_name}
Our Product: SalesEdge
Deal Context: {deal_context}
Customer Industry: {industry}
Customer Size: {company_size}

Known Competitor Strengths: {competitor_strengths}
Known Competitor Weaknesses: {competitor_weaknesses}
Recent Competitor News: {competitor_news}

Generate a battlecard with:
1. Competitor overview (2-3 sentences)
2. Their key strengths (3-5 points)
3. Our advantages over them (3-5 points)
4. Common objections and rebuttals (3-5)
5. Pricing positioning guidance
6. Win strategy specific to this deal

Respond in JSON with the sections above as keys."""
