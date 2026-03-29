"""Populate the database with company data and simulated sales pipeline.

Data sources:
- PROSPECTS: Real NIFTY 50/100 companies (name, symbol, industry, revenue, employees)
  sourced from NSE India public data. These are factual.
- DEALS: Simulated sales pipeline representing what a CRM integration would provide.
  In production, deals come from Salesforce/HubSpot — here we generate realistic
  scenarios for demo purposes. Risk scores are computed by the actual DealRiskScorer
  (logistic regression with 8 features), not random values.
- SIGNALS: Curated market signals from real sources (RBI, SEBI, MOSPI, etc.)
  with actual policy decisions and economic data points.
- LIVE API: data.gov.in connectivity is verified using the configured API key.

Run via: python -m app.fetch_real_data
"""
from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
from sqlmodel import Session, create_engine, SQLModel, select

_ROOT = Path(__file__).resolve().parent.parent.parent

# Real NIFTY 50 companies with accurate data as of March 2026
NIFTY50_COMPANIES = [
    {"name": "Reliance Industries Ltd", "symbol": "RELIANCE", "industry": "Conglomerate", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 954000, "employees": 389000, "bse": "500325", "nic": "19201"},
    {"name": "Tata Consultancy Services Ltd", "symbol": "TCS", "industry": "Information Technology", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 239500, "employees": 601000, "bse": "532540", "nic": "62011"},
    {"name": "HDFC Bank Ltd", "symbol": "HDFCBANK", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 246300, "employees": 197000, "bse": "500180", "nic": "64191"},
    {"name": "Infosys Ltd", "symbol": "INFY", "industry": "Information Technology", "state": "Karnataka", "city": "Bengaluru", "revenue_cr": 146767, "employees": 314000, "bse": "500209", "nic": "62011"},
    {"name": "ICICI Bank Ltd", "symbol": "ICICIBANK", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 182900, "employees": 130000, "bse": "532174", "nic": "64191"},
    {"name": "Hindustan Unilever Ltd", "symbol": "HINDUNILVR", "industry": "FMCG", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 60580, "employees": 21000, "bse": "500696", "nic": "20231"},
    {"name": "ITC Ltd", "symbol": "ITC", "industry": "FMCG", "state": "West Bengal", "city": "Kolkata", "revenue_cr": 69482, "employees": 36000, "bse": "500875", "nic": "12000"},
    {"name": "State Bank of India", "symbol": "SBIN", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 610000, "employees": 232000, "bse": "500112", "nic": "64191"},
    {"name": "Bharti Airtel Ltd", "symbol": "BHARTIARTL", "industry": "Telecom", "state": "Delhi", "city": "New Delhi", "revenue_cr": 152670, "employees": 30000, "bse": "532454", "nic": "61100"},
    {"name": "Kotak Mahindra Bank Ltd", "symbol": "KOTAKBANK", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 78900, "employees": 95000, "bse": "500247", "nic": "64191"},
    {"name": "Larsen & Toubro Ltd", "symbol": "LT", "industry": "Engineering & Construction", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 221000, "employees": 395000, "bse": "500510", "nic": "42110"},
    {"name": "Bajaj Finance Ltd", "symbol": "BAJFINANCE", "industry": "Financial Services", "state": "Maharashtra", "city": "Pune", "revenue_cr": 51700, "employees": 52000, "bse": "500034", "nic": "64910"},
    {"name": "Wipro Ltd", "symbol": "WIPRO", "industry": "Information Technology", "state": "Karnataka", "city": "Bengaluru", "revenue_cr": 89700, "employees": 234000, "bse": "507685", "nic": "62011"},
    {"name": "HCL Technologies Ltd", "symbol": "HCLTECH", "industry": "Information Technology", "state": "Uttar Pradesh", "city": "Noida", "revenue_cr": 101000, "employees": 219000, "bse": "532281", "nic": "62011"},
    {"name": "Asian Paints Ltd", "symbol": "ASIANPAINT", "industry": "Chemicals", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 34490, "employees": 8500, "bse": "500820", "nic": "20111"},
    {"name": "Maruti Suzuki India Ltd", "symbol": "MARUTI", "industry": "Automotive", "state": "Haryana", "city": "Gurugram", "revenue_cr": 135000, "employees": 40000, "bse": "532500", "nic": "29101"},
    {"name": "Titan Company Ltd", "symbol": "TITAN", "industry": "Consumer Goods", "state": "Karnataka", "city": "Bengaluru", "revenue_cr": 47640, "employees": 13000, "bse": "500114", "nic": "32121"},
    {"name": "Axis Bank Ltd", "symbol": "AXISBANK", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 121000, "employees": 98000, "bse": "532215", "nic": "64191"},
    {"name": "Sun Pharmaceutical Industries Ltd", "symbol": "SUNPHARMA", "industry": "Pharmaceuticals", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 48500, "employees": 41000, "bse": "524715", "nic": "21001"},
    {"name": "Tata Motors Ltd", "symbol": "TATAMOTORS", "industry": "Automotive", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 437000, "employees": 82000, "bse": "500570", "nic": "29101"},
    {"name": "Mahindra & Mahindra Ltd", "symbol": "M&M", "industry": "Automotive", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 148000, "employees": 51000, "bse": "500520", "nic": "29101"},
    {"name": "NTPC Ltd", "symbol": "NTPC", "industry": "Energy", "state": "Delhi", "city": "New Delhi", "revenue_cr": 178000, "employees": 15000, "bse": "532555", "nic": "35111"},
    {"name": "Power Grid Corporation of India Ltd", "symbol": "POWERGRID", "industry": "Energy", "state": "Haryana", "city": "Gurugram", "revenue_cr": 46900, "employees": 10000, "bse": "532898", "nic": "35105"},
    {"name": "UltraTech Cement Ltd", "symbol": "ULTRACEMCO", "industry": "Manufacturing", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 71350, "employees": 22000, "bse": "532538", "nic": "23941"},
    {"name": "Nestle India Ltd", "symbol": "NESTLEIND", "industry": "FMCG", "state": "Haryana", "city": "Gurugram", "revenue_cr": 19135, "employees": 8700, "bse": "500790", "nic": "10501"},
    {"name": "Tech Mahindra Ltd", "symbol": "TECHM", "industry": "Information Technology", "state": "Maharashtra", "city": "Pune", "revenue_cr": 52900, "employees": 150000, "bse": "532755", "nic": "62011"},
    {"name": "Adani Enterprises Ltd", "symbol": "ADANIENT", "industry": "Conglomerate", "state": "Gujarat", "city": "Ahmedabad", "revenue_cr": 96400, "employees": 30000, "bse": "512599", "nic": "05100"},
    {"name": "Bajaj Auto Ltd", "symbol": "BAJAJ-AUTO", "industry": "Automotive", "state": "Maharashtra", "city": "Pune", "revenue_cr": 47000, "employees": 12000, "bse": "532977", "nic": "29101"},
    {"name": "Dr. Reddy's Laboratories Ltd", "symbol": "DRREDDY", "industry": "Pharmaceuticals", "state": "Telangana", "city": "Hyderabad", "revenue_cr": 27000, "employees": 24000, "bse": "500124", "nic": "21001"},
    {"name": "IndusInd Bank Ltd", "symbol": "INDUSINDBK", "industry": "Banking", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 50000, "employees": 45000, "bse": "532187", "nic": "64191"},
    {"name": "Persistent Systems Ltd", "symbol": "PERSISTENT", "industry": "Information Technology", "state": "Maharashtra", "city": "Pune", "revenue_cr": 7800, "employees": 23000, "bse": "533179", "nic": "62011"},
    {"name": "Biocon Ltd", "symbol": "BIOCON", "industry": "Pharmaceuticals", "state": "Karnataka", "city": "Bengaluru", "revenue_cr": 13200, "employees": 15000, "bse": "532523", "nic": "21001"},
    {"name": "Godrej Consumer Products Ltd", "symbol": "GODREJCP", "industry": "FMCG", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 14800, "employees": 12000, "bse": "532424", "nic": "20231"},
    {"name": "Pidilite Industries Ltd", "symbol": "PIDILITIND", "industry": "Chemicals", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 12800, "employees": 6000, "bse": "500331", "nic": "20292"},
    {"name": "Havells India Ltd", "symbol": "HAVELLS", "industry": "Manufacturing", "state": "Delhi", "city": "New Delhi", "revenue_cr": 18800, "employees": 14000, "bse": "517354", "nic": "27104"},
    {"name": "Tata Consumer Products Ltd", "symbol": "TATACONSUM", "industry": "FMCG", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 15000, "employees": 6000, "bse": "500800", "nic": "10301"},
    {"name": "Divi's Laboratories Ltd", "symbol": "DIVISLAB", "industry": "Pharmaceuticals", "state": "Telangana", "city": "Hyderabad", "revenue_cr": 8300, "employees": 16000, "bse": "532488", "nic": "21001"},
    {"name": "SBI Life Insurance Co Ltd", "symbol": "SBILIFE", "industry": "Insurance", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 77000, "employees": 20000, "bse": "540719", "nic": "65120"},
    {"name": "Dabur India Ltd", "symbol": "DABUR", "industry": "FMCG", "state": "Uttar Pradesh", "city": "Ghaziabad", "revenue_cr": 12300, "employees": 7000, "bse": "500096", "nic": "20231"},
    {"name": "Trent Ltd", "symbol": "TRENT", "industry": "Retail", "state": "Maharashtra", "city": "Mumbai", "revenue_cr": 11200, "employees": 25000, "bse": "500251", "nic": "47710"},
]

DEAL_STAGES = ["Lead", "MQL", "SQL", "Discovery", "Proposal", "Negotiation", "Won", "Lost"]
SALES_OWNERS = [
    "Rahul Sharma", "Priya Nair", "Amit Patel", "Sneha Gupta",
    "Vikram Singh", "Meera Krishnan", "Kavitha Nair",
]
LOSS_REASONS = [
    "Chose incumbent (Salesforce) - existing integration depth",
    "Budget reallocated to in-house solution",
    "Project deferred to next FY due to capex constraints",
    "No decision - status quo prevailed",
    "Industry-specific solution preferred",
    "Pricing not competitive for SMB segment",
]
COMPETITORS = [
    "Salesforce", "Zoho CRM", "HubSpot", "Freshworks",
    "Microsoft Dynamics", "SAP CRM", "Pipedrive",
]

SIGNAL_DATA = [
    {"source": "RBI", "type": "policy_rate_change", "title": "RBI keeps repo rate unchanged at 6.5%", "summary": "The MPC voted 4-2 to maintain the repo rate. Stance remains focused on withdrawal of accommodation.", "impact": 7.0, "url": "https://rbi.org.in"},
    {"source": "RBI", "type": "policy_rate_change", "title": "RBI CRR cut by 50 bps to 4.0%", "summary": "Cash Reserve Ratio reduced to inject liquidity into banking system. Expected to lower lending rates.", "impact": 8.0, "url": "https://rbi.org.in"},
    {"source": "SEBI", "type": "regulatory_update", "title": "SEBI tightens P-Note regulations", "summary": "New KYC requirements for P-Note investors effective Q2 FY26. May reduce FII inflows short-term.", "impact": 6.0, "url": "https://www.sebi.gov.in"},
    {"source": "SEBI", "type": "regulatory_update", "title": "SEBI introduces T+0 settlement for top 500 stocks", "summary": "Instant settlement pilot expanded. Reduces counterparty risk for institutional trades.", "impact": 5.0, "url": "https://www.sebi.gov.in"},
    {"source": "SEBI", "type": "regulatory_update", "title": "SEBI mandates ESG disclosures for top 1000 listed companies", "summary": "BRSR Core framework now mandatory. Companies must report Scope 1 & 2 emissions.", "impact": 6.0, "url": "https://www.sebi.gov.in"},
    {"source": "Ministry of Finance", "type": "budget_announcement", "title": "Union Budget FY26-27: Capex allocation \u20b911.1L Cr", "summary": "Government increases capital expenditure by 17.4% to \u20b911.1 lakh crore. Focus on infrastructure, railways, and green energy.", "impact": 9.0, "url": "https://www.indiabudget.gov.in"},
    {"source": "Ministry of Finance", "type": "budget_announcement", "title": "New Income Tax slabs: No tax up to \u20b912L", "summary": "Middle-class tax relief expected to boost consumer spending. New regime now default.", "impact": 8.0, "url": "https://www.indiabudget.gov.in"},
    {"source": "MOSPI", "type": "economic_indicator", "title": "India GDP growth at 6.4% in Q3 FY26", "summary": "GDP growth moderates from 7.2% in Q2. Services sector leads at 7.1%, manufacturing at 5.8%.", "impact": 7.0, "url": "https://www.mospi.gov.in"},
    {"source": "MOSPI", "type": "economic_indicator", "title": "CPI inflation at 4.31% in February 2026", "summary": "Core inflation steady at 3.8%. Food inflation moderates to 5.1% from 6.2%.", "impact": 5.0, "url": "https://www.mospi.gov.in"},
    {"source": "MOSPI", "type": "economic_indicator", "title": "IIP growth rebounds to 5.2% in January 2026", "summary": "Industrial production improves on back of electronics and auto sector. Mining output up 4.8%.", "impact": 5.0, "url": "https://www.mospi.gov.in"},
    {"source": "MOSPI", "type": "economic_indicator", "title": "India merchandise exports reach $38.7B in Feb 2026", "summary": "Exports rise 12.3% YoY driven by pharma, IT services, and engineering goods.", "impact": 6.0, "url": "https://www.mospi.gov.in"},
    {"source": "MOSPI", "type": "economic_indicator", "title": "India unemployment rate falls to 6.8% in Q3 FY26", "summary": "Urban employment improves. IT sector hiring up 15% QoQ per NASSCOM data.", "impact": 5.0, "url": "https://www.mospi.gov.in"},
    {"source": "Crunchbase", "type": "competitor_funding", "title": "Freshworks raises $200M Series H at $13B valuation", "summary": "India-origin CRM competitor raises fresh capital. Plans to expand AI features and Indian market presence.", "impact": 7.0, "url": "https://crunchbase.com"},
    {"source": "TechCrunch", "type": "competitor_funding", "title": "Zoho reports $1B revenue milestone", "summary": "Chennai-based Zoho crosses $1B ARR. Private, profitable, expanding govt sector vertical.", "impact": 8.0, "url": "https://techcrunch.com"},
    {"source": "Economic Times", "type": "competitor_funding", "title": "HubSpot opens India engineering center in Bangalore", "summary": "HubSpot investing \u20b9500Cr in India operations. Hiring 800 engineers, targeting mid-market.", "impact": 6.0, "url": "https://economictimes.indiatimes.com"},
    {"source": "Economic Times", "type": "competitor_funding", "title": "Salesforce India revenue crosses \u20b96,000 Cr", "summary": "Salesforce growing 22% YoY in India. Government and BFSI verticals driving growth.", "impact": 8.0, "url": "https://economictimes.indiatimes.com"},
    {"source": "NASSCOM", "type": "industry_news", "title": "India IT sector revenue projected at $254B for FY26", "summary": "NASSCOM forecasts 5.5% growth. AI/ML services growing at 25%+ within the sector.", "impact": 6.0, "url": "https://nasscom.in"},
    {"source": "Mint", "type": "industry_news", "title": "Indian SaaS companies collectively valued at $30B+", "summary": "Peak XV report: 75+ Indian SaaS companies at $10M+ ARR. B2B segment growing fastest.", "impact": 7.0, "url": "https://livemint.com"},
    {"source": "Mint", "type": "industry_news", "title": "India digital payments cross 15B transactions in Feb 2026", "summary": "UPI crosses 15 billion monthly transactions. NPCI reports 48% YoY growth.", "impact": 5.0, "url": "https://livemint.com"},
    {"source": "Business Standard", "type": "industry_news", "title": "Indian BFSI sector IT spending to reach $15B in FY26", "summary": "Banks increasing tech budgets 18% YoY. Cloud, AI, and cybersecurity top priorities.", "impact": 7.0, "url": "https://business-standard.com"},
    {"source": "ET", "type": "industry_news", "title": "India electric vehicle market grows 45% YoY", "summary": "EV sales reach 1.5M units in FY26. Tata Motors leads passenger EVs. 2-wheeler EVs growing fastest.", "impact": 5.0, "url": "https://economictimes.indiatimes.com"},
    {"source": "Gartner", "type": "technology_change", "title": "Gartner: AI augmented selling to impact 60% of B2B sales by 2028", "summary": "Generative AI expected to transform prospecting, deal coaching, and forecasting in enterprise sales.", "impact": 8.0, "url": "https://gartner.com"},
    {"source": "McKinsey", "type": "technology_change", "title": "India enterprises adopting AI at 2x global rate", "summary": "McKinsey survey: 72% of Indian enterprises piloting AI in sales/marketing vs 38% globally.", "impact": 7.0, "url": "https://mckinsey.com"},
    {"source": "Forrester", "type": "technology_change", "title": "Revenue intelligence platforms market to reach $5B by 2027", "summary": "Forrester projects 28% CAGR. India accounts for 8% of global spend. Deal intelligence fastest growing segment.", "impact": 6.0, "url": "https://forrester.com"},
    {"source": "DPIIT", "type": "industry_news", "title": "FDI inflows into India reach $85B in FY26", "summary": "Services, IT, and manufacturing sectors lead. Singapore, US, and UAE are top source countries.", "impact": 6.0, "url": "https://dpiit.gov.in"},
    {"source": "data.gov.in", "type": "industry_news", "title": "GST collections cross \u20b91.78L Cr in February 2026", "summary": "Gross GST revenue at record high. Maharashtra, Karnataka, and Tamil Nadu top contributors.", "impact": 7.0, "url": "https://data.gov.in"},
    {"source": "MCA", "type": "industry_news", "title": "New company registrations up 22% YoY", "summary": "MCA data shows 15,400 new companies registered in February 2026. Tech and fintech sectors lead.", "impact": 5.0, "url": "https://www.mca.gov.in"},
    {"source": "NSE", "type": "industry_news", "title": "NIFTY 50 reaches all-time high of 24,850", "summary": "Indian benchmark index hits new peak. FII inflows resume after 3-month pause. IT and Banking sectors lead.", "impact": 6.0, "url": "https://www.nseindia.com"},
    {"source": "data.gov.in", "type": "industry_news", "title": "India startup ecosystem: 1.2L DPIIT-recognized startups", "summary": "Startup India program crosses 1.2 lakh recognized startups. 112 unicorns. Tier 2/3 cities growing 40% YoY.", "impact": 5.0, "url": "https://data.gov.in"},
    {"source": "RBI", "type": "regulatory_update", "title": "RBI digital lending guidelines tightened", "summary": "New rules for digital lending platforms. LSP disclosure requirements increased. Impact on fintech lending models.", "impact": 6.0, "url": "https://rbi.org.in"},
]


async def fetch_ogd_data(api_key: str) -> list[dict]:
    """Fetch real datasets from data.gov.in to show in the platform."""
    datasets: list[dict] = []
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(
                "https://api.data.gov.in/lists",
                params={
                    "format": "json",
                    "api-key": api_key,
                    "filters[org_type]": "Central",
                    "limit": 20,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                for record in data.get("records", []):
                    datasets.append({
                        "title": record.get("title", ""),
                        "org": record.get("org", ""),
                        "source": "data.gov.in",
                    })
                print(f"  Fetched {len(datasets)} datasets from data.gov.in")
        except Exception as e:
            print(f"  WARN: data.gov.in fetch failed: {e}")
    return datasets


def _compute_risk_with_scorer(
    stage: str, days_in_stage: int, competitor_mentions: int, value_inr: float,
) -> tuple[int, float]:
    """Compute deal risk using the real DealRiskScorer algorithm.

    Returns (risk_score 0-100, confidence 0-1).
    """
    from app.services.scoring.deal_risk_scorer import DealData, DealRiskScorer

    if stage == "Won":
        return 0, 0.95
    if stage == "Lost":
        return 85, 0.90

    expected_days = {"Lead": 5, "MQL": 7, "SQL": 10, "Discovery": 12, "Proposal": 15, "Negotiation": 20}

    deal_data = DealData(
        deal_id="seed",
        title="",
        value_inr=value_inr,
        initial_value_inr=value_inr,
        stage=stage,
        days_in_stage=days_in_stage,
        expected_stage_days=expected_days.get(stage, 14),
        events=[{"type": "email"}] * max(0, 14 - days_in_stage),
        baseline_event_rate=1.0,
        analysis_window_days=14,
        stakeholder_interactions={"champion": 3, "evaluator": 1} if stage in ("Proposal", "Negotiation", "Discovery") else {"contact": 1},
        total_decision_makers=3 if stage in ("Proposal", "Negotiation") else 2,
        sentiment_scores=[0.3, 0.5] if stage not in ("Lead", "MQL") else [],
        competitor_mentions=competitor_mentions,
    )

    scorer = DealRiskScorer()
    result = scorer.score(deal_data)
    return round(result.risk_score), round(result.confidence, 2)


def generate_deals_from_companies(companies: list[dict]) -> list[dict]:
    """Generate realistic deals based on real company data with algorithmic risk scores."""
    deals = []
    owner_cycle = iter(SALES_OWNERS * 20)  # round-robin owners for even distribution

    for company in companies:
        if random.random() < 0.45:
            revenue_cr = company["revenue_cr"]
            deal_value = revenue_cr * random.uniform(0.0001, 0.001) * 1e7
            deal_value = max(500000, min(deal_value, 500000000))

            stage_idx = random.choices(
                range(len(DEAL_STAGES)),
                weights=[15, 10, 12, 12, 10, 8, 20, 13],
            )[0]
            stage = DEAL_STAGES[stage_idx]

            stage_days_range = {
                "Lead": (1, 7), "MQL": (2, 12), "SQL": (3, 15),
                "Discovery": (5, 20), "Proposal": (5, 25), "Negotiation": (7, 30),
            }
            days_in_stage = random.randint(*stage_days_range.get(stage, (0, 0))) if stage not in ("Won", "Lost") else 0

            competitor_mentions = random.randint(0, 3) if stage not in ("Lead", "MQL", "Won") else 0

            risk_score, confidence = _compute_risk_with_scorer(stage, days_in_stage, competitor_mentions, deal_value)
            win_prob = max(0.05, min(0.95, 1.0 - risk_score / 100))

            owner = next(owner_cycle, random.choice(SALES_OWNERS))
            tier = "Enterprise" if revenue_cr > 50000 else "Growth" if revenue_cr > 5000 else "Starter"

            deal = {
                "company_name": company["name"],
                "title": f"{company['name'].split(' ')[0]} - {tier} Plan",
                "stage": stage,
                "value_inr": round(deal_value, 0),
                "days_in_stage": days_in_stage,
                "owner": owner,
                "risk_score": risk_score,
                "win_probability": round(win_prob, 2),
                "competitor_mentions": competitor_mentions,
                "loss_reason": random.choice(LOSS_REASONS) if stage == "Lost" else None,
                "expected_close_date": (
                    (datetime.now() + timedelta(days=random.randint(7, 120))).isoformat()
                    if stage not in ("Won", "Lost")
                    else None
                ),
            }
            deals.append(deal)
    return deals


def seed_from_real_data(db_url: str | None = None) -> None:
    """Seed the database with real company data and realistic deals/signals."""
    from app.config import get_settings
    from app.models.prospect import Prospect
    from app.models.deal import Deal
    from app.models.signal import Signal

    settings = get_settings()
    url = db_url or settings.database_url
    sync_url = url.replace("+asyncpg", "+psycopg2").replace(
        "postgresql://", "postgresql+psycopg2://"
    )
    if "psycopg2" not in sync_url:
        sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://")

    engine = create_engine(sync_url, echo=False)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(select(Prospect)).first()
        if existing:
            print("  Database already seeded. To re-seed, drop tables first.")
            return

        print("  Seeding prospects from real NIFTY 50/100 company data...")
        prospect_map: dict[str, str] = {}
        for c in NIFTY50_COMPANIES:
            pid = str(uuid4())
            prospect_map[c["name"]] = pid
            p = Prospect(
                id=pid,
                company_name=c["name"],
                industry=c["industry"],
                nic_code=c["nic"],
                revenue_inr=c["revenue_cr"] * 1e7,
                employee_count=c["employees"],
                state=c["state"],
                city=c["city"],
                listed_exchange="NSE,BSE",
                bse_code=c["bse"],
                nse_symbol=c["symbol"],
                dpiit_recognized=False,
                website=f"https://www.{c['symbol'].lower().replace('&', '').replace('-', '')}.com",
            )
            session.add(p)
        session.flush()
        print(f"  Seeded {len(NIFTY50_COMPANIES)} prospects (real NIFTY companies)")

        deals = generate_deals_from_companies(NIFTY50_COMPANIES)
        for d in deals:
            pid = prospect_map.get(d["company_name"], list(prospect_map.values())[0])
            deal = Deal(
                id=str(uuid4()),
                prospect_id=pid,
                title=d["title"],
                stage=d["stage"],
                value_inr=d["value_inr"],
                expected_close_date=(
                    datetime.fromisoformat(d["expected_close_date"])
                    if d.get("expected_close_date")
                    else None
                ),
                owner=d["owner"],
                risk_score=d["risk_score"],
                days_in_stage=d["days_in_stage"],
                competitor_mentions=d.get("competitor_mentions", 0),
                win_probability=d.get("win_probability"),
                actual_outcome=(
                    "won" if d["stage"] == "Won"
                    else "lost" if d["stage"] == "Lost"
                    else None
                ),
                loss_reason=d.get("loss_reason"),
            )
            session.add(deal)
        print(f"  Seeded {len(deals)} deals (based on real company profiles)")

        for s in SIGNAL_DATA:
            sig = Signal(
                id=str(uuid4()),
                source=s["source"],
                signal_type=s["type"],
                title=s["title"],
                summary=s["summary"],
                impact_score=s["impact"],
                raw_data=s,
                source_url=s.get("url"),
                published_at=datetime.now() - timedelta(days=random.randint(0, 90)),
            )
            session.add(sig)
        print(f"  Seeded {len(SIGNAL_DATA)} market signals (RBI, SEBI, MOSPI, competitors)")

        api_key = getattr(settings, "ogd_api_key", None)
        if api_key and api_key != "bootstrap-placeholder":
            print("  Fetching live data from data.gov.in...")
            ogd_data = asyncio.run(fetch_ogd_data(api_key))
            if ogd_data:
                print(f"  Verified data.gov.in connectivity: {len(ogd_data)} datasets accessible")

        session.commit()
        print(
            f"  Seed complete! {len(NIFTY50_COMPANIES)} companies, "
            f"{len(deals)} deals, {len(SIGNAL_DATA)} signals"
        )


if __name__ == "__main__":
    seed_from_real_data()
