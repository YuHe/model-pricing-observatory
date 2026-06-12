from __future__ import annotations
import pytest
from decimal import Decimal
from app.crawlers.siliconflow import SiliconFlowCrawler
from app.crawlers.together import TogetherCrawler
from app.crawlers.groq import GroqCrawler


SILICONFLOW_RESPONSE = {
    "data": [
        {"id": "deepseek-ai/DeepSeek-V3", "pricing": {"input": "0.000001", "output": "0.000002"}},
        {"id": "Qwen/Qwen2.5-72B-Instruct", "pricing": {"input": "0.0000004", "output": "0.0000004"}},
    ]
}

TOGETHER_RESPONSE = {
    "data": [
        {"id": "meta-llama/Meta-Llama-3.1-405B", "pricing": {"input": 0.000003, "output": 0.000003}},
    ]
}

GROQ_RESPONSE = {
    "data": [
        {"id": "llama-3.3-70b-versatile", "pricing": {"input": 0.00000059, "output": 0.00000079}},
    ]
}


def test_siliconflow_parse():
    results = SiliconFlowCrawler._parse_response(SILICONFLOW_RESPONSE)
    assert len(results) >= 1
    ds = next((r for r in results if "deepseek" in r["name"].lower()), None)
    assert ds is not None
    # 0.000001 $/token * 1M = $1/M
    assert ds["input_price"] == Decimal("1")


def test_together_parse():
    results = TogetherCrawler._parse_response(TOGETHER_RESPONSE)
    assert len(results) >= 1
    llama = results[0]
    # 0.000003 * 1M = $3/M
    assert llama["input_price"] == Decimal("3")


def test_groq_parse():
    results = GroqCrawler._parse_response(GROQ_RESPONSE)
    assert len(results) >= 1
