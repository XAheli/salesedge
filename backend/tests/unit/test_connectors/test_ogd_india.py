from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from app.connectors.government.ogd_india import OGDIndiaConnector


@pytest_asyncio.fixture
async def connector():
    c = OGDIndiaConnector(api_key="test-ogd-api-key")
    yield c
    await c.close()


@pytest.fixture
def mock_response_search():
    return {
        "records": [
            {"title": "GDP Data", "org": "MOSPI", "source": "data.gov.in"},
            {"title": "CPI Data", "org": "MOSPI", "source": "data.gov.in"},
        ],
        "total": 2,
    }


@pytest.fixture
def mock_response_resource():
    return {
        "records": [
            {"state": "Maharashtra", "value": "1234.5"},
            {"state": "Karnataka", "value": "987.3"},
        ],
        "fields": [
            {"id": "state", "name": "State"},
            {"id": "value", "name": "Value"},
        ],
        "total": 50,
    }


class TestOGDIndiaConnector:
    def test_init(self, connector):
        assert connector.name == "ogd_india"
        assert connector._api_key == "test-ogd-api-key"
        assert "api.data.gov.in" in connector.base_url

    def test_apply_auth(self, connector):
        headers = {}
        params = {}
        connector._apply_auth(headers, params)
        assert params["api-key"] == "test-ogd-api-key"

    @pytest.mark.asyncio
    async def test_search_datasets(self, connector, mock_response_search):
        connector._request = AsyncMock(return_value=mock_response_search)
        result = await connector.search_datasets("GDP", ministry="MOSPI")
        assert result["total"] == 2
        assert len(result["records"]) == 2
        connector._request.assert_called_once()
        call_kwargs = connector._request.call_args
        assert call_kwargs[0][0] == "GET"
        assert call_kwargs[0][1] == "/lists"

    @pytest.mark.asyncio
    async def test_search_datasets_with_filters(self, connector, mock_response_search):
        connector._request = AsyncMock(return_value=mock_response_search)
        result = await connector.search_datasets(
            "inflation", department="Statistics", limit=50, offset=10,
        )
        call_kwargs = connector._request.call_args
        params = call_kwargs[1]["params"]
        assert params["search"] == "inflation"
        assert params["filters[department]"] == "Statistics"
        assert params["limit"] == 50
        assert params["offset"] == 10

    @pytest.mark.asyncio
    async def test_get_resource(self, connector, mock_response_resource):
        connector._request = AsyncMock(return_value=mock_response_resource)
        result = await connector.get_resource("abc123", fmt="json", limit=100)
        assert len(result["records"]) == 2
        connector._request.assert_called_once()
        call_args = connector._request.call_args
        assert "/resource/abc123" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_get_resource_with_filters(self, connector, mock_response_resource):
        connector._request = AsyncMock(return_value=mock_response_resource)
        await connector.get_resource(
            "abc123", filters={"state": "Maharashtra"},
        )
        call_kwargs = connector._request.call_args
        params = call_kwargs[1]["params"]
        assert params["filters[state]"] == "Maharashtra"

    @pytest.mark.asyncio
    async def test_list_catalogs(self, connector):
        mock_catalogs = {"records": [{"name": "Economic"}], "total": 1}
        connector._request = AsyncMock(return_value=mock_catalogs)
        result = await connector.list_catalogs(limit=10)
        assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_discover_datasets_by_ministry(self, connector, mock_response_search):
        connector.search_datasets = AsyncMock(return_value=mock_response_search)
        results = await connector.discover_datasets_by_ministry("MOSPI", page_size=10)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_discover_stops_on_exhaustion(self, connector):
        page1 = {"records": [{"id": 1}], "total": 1}
        connector.search_datasets = AsyncMock(return_value=page1)
        results = await connector.discover_datasets_by_ministry("RBI", page_size=100)
        assert len(results) == 1
        connector.search_datasets.assert_called_once()

    @pytest.mark.asyncio
    async def test_discover_handles_exception(self, connector):
        connector.search_datasets = AsyncMock(side_effect=Exception("Network error"))
        results = await connector.discover_datasets_by_ministry("RBI")
        assert results == []


class TestDataQualityScoring:
    def test_high_quality_data(self, connector):
        resource_data = {
            "records": [
                {"state": "MH", "gdp": "1234.5", "pop": "112374333"},
                {"state": "KA", "gdp": "987.3", "pop": "61095297"},
            ],
            "fields": [
                {"id": "state"}, {"id": "gdp"}, {"id": "pop"},
            ],
            "total": 100,
        }
        result = connector.score_data_quality(resource_data)
        assert result["quality_tier"] == "high"
        assert result["completeness"] > 0.85
        assert result["record_count"] == 2
        assert result["total_available"] == 100

    def test_low_quality_data(self, connector):
        resource_data = {
            "records": [
                {"state": "MH", "gdp": None, "pop": "NA"},
                {"state": None, "gdp": "", "pop": "N/A"},
            ],
            "fields": [
                {"id": "state"}, {"id": "gdp"}, {"id": "pop"},
            ],
            "total": 50,
        }
        result = connector.score_data_quality(resource_data)
        assert result["quality_tier"] in ("low", "medium")
        assert result["completeness"] < 0.5

    def test_empty_records(self, connector):
        resource_data = {"records": [], "fields": [], "total": 0}
        result = connector.score_data_quality(resource_data)
        assert result["record_count"] == 0

    def test_business_use_cases(self, connector):
        cases = connector.get_business_use_cases()
        assert "prospect_research" in cases
        assert "macro_context" in cases


class TestCacheKey:
    def test_deterministic(self, connector):
        key1 = connector._cache_key("search", {"q": "gdp", "limit": 10})
        key2 = connector._cache_key("search", {"q": "gdp", "limit": 10})
        assert key1 == key2

    def test_different_params_different_key(self, connector):
        key1 = connector._cache_key("search", {"q": "gdp"})
        key2 = connector._cache_key("search", {"q": "cpi"})
        assert key1 != key2

    def test_key_starts_with_prefix(self, connector):
        key = connector._cache_key("search", {"q": "test"})
        assert key.startswith("ogd:search:")
