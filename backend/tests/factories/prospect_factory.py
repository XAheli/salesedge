from __future__ import annotations

import random
from datetime import datetime, timedelta
from uuid import uuid4

import factory
from factory import fuzzy

from app.models.prospect import Prospect

_INDIAN_COMPANIES = [
    "Aditya Systems Pvt Ltd", "Bharat Infotech Solutions", "Chakra Innovations Pvt Ltd",
    "Dhanush Technologies Pvt Ltd", "Ekam Software Services", "Falcon Analytics Pvt Ltd",
    "Garuda Cloud Pvt Ltd", "Hari Enterprise Solutions", "Indra Digital Pvt Ltd",
    "Jyoti Financial Systems", "Kaveri Data Corp", "Lakshya Tech Pvt Ltd",
    "Mantra Infoservices Pvt Ltd", "Narmada Solutions Pvt Ltd", "Om Prakash Industries",
    "Pavan Systems Pvt Ltd", "Qutub Digital Pvt Ltd", "Rishi Fintech Pvt Ltd",
    "Sagar Consulting Services", "Tara Analytics Pvt Ltd", "Uday Software Solutions",
    "Veda Infotech Pvt Ltd", "Wadhwa Business Systems", "Xcel India Technologies",
    "Yaksha Cloud Services Pvt Ltd", "Zenith Digital India Pvt Ltd",
]

_INDUSTRIES = [
    "Information Technology", "Banking", "Financial Services", "Pharmaceuticals",
    "Automotive", "FMCG", "Energy", "Real Estate", "Telecommunications",
    "Manufacturing", "Retail", "Education", "Healthcare", "Logistics",
]

_NIC_CODES = ["62011", "62013", "64191", "64920", "21001", "29100", "20231", "41001"]

_STATES = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Telangana",
           "Gujarat", "Uttar Pradesh", "West Bengal", "Haryana", "Kerala",
           "Rajasthan", "Punjab"]

_STATE_CODES = ["MH", "KA", "TN", "DL", "TG", "GJ", "UP", "WB", "HR", "KL", "RJ", "PB"]

_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
    "Karnataka": ["Bengaluru", "Mysuru"],
    "Tamil Nadu": ["Chennai", "Coimbatore"],
    "Delhi": ["New Delhi"],
    "Telangana": ["Hyderabad"],
    "Gujarat": ["Ahmedabad", "Vadodara", "Surat", "Rajkot"],
    "Uttar Pradesh": ["Noida", "Lucknow"],
    "West Bengal": ["Kolkata"],
    "Haryana": ["Gurugram"],
    "Kerala": ["Kochi", "Thiruvananthapuram"],
    "Rajasthan": ["Jaipur"],
    "Punjab": ["Ludhiana", "Chandigarh"],
}


class ProspectFactory(factory.Factory):
    """Factory for generating realistic Indian prospect records."""

    class Meta:
        model = Prospect

    id = factory.LazyFunction(uuid4)
    company_name = fuzzy.FuzzyChoice(_INDIAN_COMPANIES)
    industry = fuzzy.FuzzyChoice(_INDUSTRIES)
    nic_code = fuzzy.FuzzyChoice(_NIC_CODES)
    revenue_inr = fuzzy.FuzzyFloat(1e6, 5e10)
    employee_count = fuzzy.FuzzyInteger(10, 50000)
    state = fuzzy.FuzzyChoice(_STATES)
    city = factory.LazyAttribute(lambda o: random.choice(_CITIES.get(o.state, ["Unknown"])))
    gst_number = factory.LazyAttribute(
        lambda o: f"{random.randint(10, 37):02d}AABCX{random.randint(1000, 9999)}Y1Z{random.randint(0, 9)}"
    )
    mca_registration_date = fuzzy.FuzzyDate(
        datetime(1990, 1, 1).date(), datetime(2023, 12, 31).date()
    )
    listed_exchange = None
    bse_code = None
    nse_symbol = None
    dpiit_recognized = False
    website = factory.LazyAttribute(
        lambda o: f"https://www.{o.company_name.split()[0].lower()}.com"
    )
    fit_score = fuzzy.FuzzyFloat(20.0, 95.0)
    fit_score_confidence = fuzzy.FuzzyFloat(0.4, 1.0)
    last_enriched_at = factory.LazyFunction(
        lambda: datetime.utcnow() - timedelta(days=random.randint(0, 30))
    )
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class ListedProspectFactory(ProspectFactory):
    """Prospects listed on Indian stock exchanges."""

    listed_exchange = fuzzy.FuzzyChoice(["NSE", "BSE", "NSE,BSE"])
    nse_symbol = factory.LazyAttribute(
        lambda o: o.company_name[:5].upper().replace(" ", "")
    )
    bse_code = factory.LazyAttribute(
        lambda _: str(random.randint(500000, 545000))
    )
    revenue_inr = fuzzy.FuzzyFloat(1e9, 1e12)
    employee_count = fuzzy.FuzzyInteger(1000, 300000)
    fit_score = fuzzy.FuzzyFloat(55.0, 95.0)
    fit_score_confidence = fuzzy.FuzzyFloat(0.7, 1.0)


class StartupProspectFactory(ProspectFactory):
    """DPIIT-recognised startup prospects."""

    dpiit_recognized = True
    listed_exchange = None
    bse_code = None
    nse_symbol = None
    revenue_inr = fuzzy.FuzzyFloat(1e5, 5e9)
    employee_count = fuzzy.FuzzyInteger(5, 2000)
    mca_registration_date = fuzzy.FuzzyDate(
        datetime(2016, 1, 1).date(), datetime(2025, 12, 31).date()
    )
    state = fuzzy.FuzzyChoice(["Karnataka", "Maharashtra", "Delhi", "Haryana", "Tamil Nadu"])
    fit_score = fuzzy.FuzzyFloat(40.0, 90.0)
    fit_score_confidence = fuzzy.FuzzyFloat(0.3, 0.85)
