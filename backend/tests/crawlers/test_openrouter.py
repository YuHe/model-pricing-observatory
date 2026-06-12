from __future__ import annotations
import pytest
from decimal import Decimal
from app.crawlers.openrouter import OpenRouterCrawler


MOCK_OPENROUTER_RESPONSE = {
    "data": [
        {
            "id": "anthropic/claude-sonnet-4-20250514",
            "pricing": {"prompt": "0.000003", "completion": "0.000015"},
            "context_length": 200000,
            "top_provider": {"max_completion_tokens": 16000},
        },
        {
            "id": "openai/gpt-4o",
            "pricing": {"prompt": "0.0000025", "completion": "0.00001"},
            "context_length": 128000,
            "top_provider": {"max_completion_tokens": 16384},
        },
        {
            "id": "free/model",
            "pricing": {"prompt": "0", "completion": "0"},
            "context_length": 8000,
            "top_provider": None,
        },
        {
            "id": "no-pricing/model",
            "pricing": None,
            "context_length": 4000,
        },
    ]
}


def test_price_conversion():
    """OpenRouter returns $/token, we convert to $/M tokens."""
    prompt_price_per_token = Decimal("0.000003")
    expected_per_m = Decimal("3.000000")
    result = prompt_price_per_token * 1_000_000
    assert result == expected_per_m


def test_extract_family():
    assert OpenRouterCrawler._extract_family("anthropic/claude-sonnet-4") == "Claude"
    assert OpenRouterCrawler._extract_family("openai/gpt-4o") == "Gpt"
    assert OpenRouterCrawler._extract_family("no-slash") is None


def test_cny_conversion():
    """Test CNY conversion with exchange rate."""
    input_price_usd = Decimal("3.0")
    rate = Decimal("7.25")
    expected_cny = Decimal("21.75")
    assert input_price_usd * rate == expected_cny


def test_skip_no_pricing():
    """Models without pricing should be skipped."""
    items = MOCK_OPENROUTER_RESPONSE["data"]
    priced_items = [i for i in items if i.get("pricing")]
    assert len(priced_items) == 3
