from __future__ import annotations

from decimal import Decimal

from app.crawlers.openai import OpenAICrawler
from app.crawlers.anthropic import AnthropicCrawler
from app.crawlers.google import GoogleCrawler
from app.crawlers.xai import XAICrawler
from app.crawlers.mistral import MistralCrawler
from app.crawlers.cohere import CohereCrawler


OPENAI_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>gpt-4o</td><td>$2.50 / 1M tokens</td><td>$10.00 / 1M tokens</td></tr>
<tr><td>gpt-4o-mini</td><td>$0.15 / 1M tokens</td><td>$0.60 / 1M tokens</td></tr></table>'''

ANTHROPIC_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>Claude Sonnet 4</td><td>$3 / MTok</td><td>$15 / MTok</td></tr>
<tr><td>Claude Haiku 3.5</td><td>$0.80 / MTok</td><td>$4 / MTok</td></tr></table>'''

GOOGLE_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>Gemini 2.5 Pro</td><td>$1.25 / 1M tokens</td><td>$10.00 / 1M tokens</td></tr></table>'''

XAI_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>Grok 3</td><td>$3.00 / 1M tokens</td><td>$15.00 / 1M tokens</td></tr></table>'''

MISTRAL_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>Mistral Large</td><td>$2.00 / 1M tokens</td><td>$6.00 / 1M tokens</td></tr></table>'''

COHERE_HTML = '''<table><tr><th>Model</th><th>Input</th><th>Output</th></tr>
<tr><td>Command R+</td><td>$2.50 / 1M tokens</td><td>$10.00 / 1M tokens</td></tr></table>'''


def test_openai_parse():
    results = OpenAICrawler._parse_html(OPENAI_HTML)
    assert len(results) >= 1
    gpt4o = next((r for r in results if "gpt-4o" in r["name"].lower()), None)
    assert gpt4o is not None
    assert gpt4o["input_price"] == Decimal("2.50")
    assert gpt4o["output_price"] == Decimal("10.00")


def test_openai_parse_mini():
    results = OpenAICrawler._parse_html(OPENAI_HTML)
    mini = next((r for r in results if "mini" in r["name"].lower()), None)
    assert mini is not None
    assert mini["input_price"] == Decimal("0.15")
    assert mini["output_price"] == Decimal("0.60")


def test_anthropic_parse():
    results = AnthropicCrawler._parse_html(ANTHROPIC_HTML)
    assert len(results) >= 1
    sonnet = next((r for r in results if "sonnet" in r["name"].lower()), None)
    assert sonnet is not None
    assert sonnet["input_price"] == Decimal("3")
    assert sonnet["output_price"] == Decimal("15")


def test_google_parse():
    results = GoogleCrawler._parse_html(GOOGLE_HTML)
    assert len(results) >= 1
    pro = results[0]
    assert pro["input_price"] == Decimal("1.25")
    assert pro["output_price"] == Decimal("10.00")


def test_xai_parse():
    results = XAICrawler._parse_html(XAI_HTML)
    assert len(results) >= 1
    grok = results[0]
    assert grok["input_price"] == Decimal("3.00")
    assert grok["output_price"] == Decimal("15.00")


def test_mistral_parse():
    results = MistralCrawler._parse_html(MISTRAL_HTML)
    assert len(results) >= 1
    large = results[0]
    assert large["input_price"] == Decimal("2.00")
    assert large["output_price"] == Decimal("6.00")


def test_cohere_parse():
    results = CohereCrawler._parse_html(COHERE_HTML)
    assert len(results) >= 1
    cmd = results[0]
    assert cmd["input_price"] == Decimal("2.50")
    assert cmd["output_price"] == Decimal("10.00")
