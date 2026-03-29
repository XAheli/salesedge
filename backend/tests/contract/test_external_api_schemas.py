"""Tests for upstream API drift detection.

Validates that responses from external data sources still match the schemas
SalesEdge's connectors expect. Uses mocked responses for CI; set
SALESEDGE_LIVE_CONTRACT_TESTS=1 to hit real APIs in nightly runs.
"""

from __future__ import annotations

import os

import pytest

LIVE_TESTS = os.environ.get("SALESEDGE_LIVE_CONTRACT_TESTS", "0") == "1"
skip_unless_live = pytest.mark.skipif(
    not LIVE_TESTS, reason="Live contract tests disabled (set SALESEDGE_LIVE_CONTRACT_TESTS=1)"
)


FINNHUB_PROFILE_FIXTURE = {
    "country": "IN",
    "currency": "INR",
    "exchange": "NSE",
    "finnhubIndustry": "Technology",
    "ipo": "1993-02-08",
    "logo": "https://example.com/logo.png",
    "marketCapitalization": 500000,
    "name": "Infosys Limited",
    "ticker": "INFY",
    "weburl": "https://www.infosys.com",
}

ALPHA_VANTAGE_QUOTE_FIXTURE = {
    "Global Quote": {
        "01. symbol": "INFY.BSE",
        "02. open": "1450.00",
        "03. high": "1480.00",
        "04. low": "1440.00",
        "05. price": "1465.50",
        "06. volume": "3200000",
        "08. previous close": "1448.00",
    }
}

OGD_DATASET_FIXTURE = {
    "records": [
        {
            "field": [
                {"id": "title", "value": "Industrial Production Index"},
                {"id": "org", "value": "MOSPI"},
            ]
        }
    ],
    "total": 1,
    "count": 1,
}


class TestFinnhubSchema:
    def test_profile_has_required_fields(self):
        required = {"name", "ticker", "country", "marketCapitalization", "finnhubIndustry"}
        assert required.issubset(FINNHUB_PROFILE_FIXTURE.keys())

    def test_market_cap_is_numeric(self):
        assert isinstance(FINNHUB_PROFILE_FIXTURE["marketCapitalization"], (int, float))

    @skip_unless_live
    @pytest.mark.asyncio
    async def test_live_finnhub_profile(self):
        import httpx

        api_key = os.environ.get("FINNHUB_API_KEY", "")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://finnhub.io/api/v1/stock/profile2",
                params={"symbol": "INFY", "token": api_key},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "name" in data
            assert "marketCapitalization" in data


class TestAlphaVantageSchema:
    def test_global_quote_structure(self):
        quote = ALPHA_VANTAGE_QUOTE_FIXTURE["Global Quote"]
        assert "05. price" in quote
        assert "06. volume" in quote

    def test_price_is_string_numeric(self):
        price = ALPHA_VANTAGE_QUOTE_FIXTURE["Global Quote"]["05. price"]
        float(price)


class TestOGDSchema:
    def test_ogd_response_has_records(self):
        assert "records" in OGD_DATASET_FIXTURE
        assert isinstance(OGD_DATASET_FIXTURE["records"], list)

    def test_ogd_record_has_fields(self):
        record = OGD_DATASET_FIXTURE["records"][0]
        assert "field" in record
        field_ids = {f["id"] for f in record["field"]}
        assert "title" in field_ids


class TestCoinGeckoSchema:
    FIXTURE = {
        "id": "bitcoin",
        "symbol": "btc",
        "name": "Bitcoin",
        "market_data": {
            "current_price": {"inr": 5500000},
            "market_cap": {"inr": 110000000000000},
        },
    }

    def test_has_market_data(self):
        assert "market_data" in self.FIXTURE
        assert "current_price" in self.FIXTURE["market_data"]

    def test_inr_price_present(self):
        assert "inr" in self.FIXTURE["market_data"]["current_price"]
