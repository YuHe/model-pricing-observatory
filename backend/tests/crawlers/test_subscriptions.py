from __future__ import annotations
import sys
from unittest.mock import MagicMock

# Mock playwright before importing the module
sys.modules.setdefault("playwright", MagicMock())
sys.modules.setdefault("playwright.async_api", MagicMock())

import pytest
from decimal import Decimal
from app.crawlers.subscriptions import SubscriptionCrawler


CURSOR_HTML = '''<div class="pricing-card">
<h3>Pro</h3><p class="price">$20/month</p>
</div>
<div class="pricing-card">
<h3>Business</h3><p class="price">$40/month</p>
</div>'''

CLAUDE_HTML = '''<div>
<span>Pro</span><span>$20/mo</span>
<span>Max</span><span>$100/mo</span>
</div>'''


def test_subscription_parse_prices():
    results = SubscriptionCrawler._parse_pricing_page(CURSOR_HTML, "Cursor")
    assert len(results) >= 1
    prices = [r["monthly_price"] for r in results]
    assert Decimal("20") in prices


def test_subscription_parse_claude():
    results = SubscriptionCrawler._parse_pricing_page(CLAUDE_HTML, "Anthropic")
    assert len(results) >= 1
    prices = [r["monthly_price"] for r in results]
    assert Decimal("20") in prices or Decimal("100") in prices
