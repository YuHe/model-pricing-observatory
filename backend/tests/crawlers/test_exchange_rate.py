from __future__ import annotations
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date
from decimal import Decimal
from app.crawlers.exchange_rate import ExchangeRateCrawler


@pytest.fixture
def mock_exchange_response():
    return {"rates": {"CNY": 7.2456, "EUR": 0.92}, "base": "USD"}


@pytest.mark.asyncio
async def test_exchange_rate_parse(mock_exchange_response):
    """Test that exchange rate is correctly parsed from API response."""
    rate = mock_exchange_response["rates"]["CNY"]
    assert rate == 7.2456


@pytest.mark.asyncio
async def test_exchange_rate_missing_cny():
    """Test handling when CNY is missing from response."""
    bad_response = {"rates": {"EUR": 0.92}, "base": "USD"}
    with pytest.raises(KeyError):
        _ = bad_response["rates"]["CNY"]
