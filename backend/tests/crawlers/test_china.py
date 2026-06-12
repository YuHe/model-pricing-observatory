from __future__ import annotations
import sys
from unittest.mock import MagicMock

# Mock playwright so imports succeed without it installed
if "playwright" not in sys.modules:
    sys.modules["playwright"] = MagicMock()
    sys.modules["playwright.async_api"] = MagicMock()

import pytest
from decimal import Decimal
from app.crawlers.deepseek import DeepSeekCrawler
from app.crawlers.qwen import QwenCrawler
from app.crawlers.glm import GLMCrawler
from app.crawlers.doubao import DoubaoCrawler
from app.crawlers.minimax import MiniMaxCrawler
from app.crawlers.ernie import ERNIECrawler
from app.crawlers.hunyuan import HunyuanCrawler
from app.crawlers.kimi import KimiCrawler
from app.crawlers.xiaomi import XiaomiCrawler


DEEPSEEK_HTML = '''<table><tr><th>模型</th><th>输入价格</th><th>输出价格</th></tr>
<tr><td>deepseek-chat</td><td>1元/百万tokens</td><td>4元/百万tokens</td></tr>
<tr><td>deepseek-reasoner</td><td>4元/百万tokens</td><td>16元/百万tokens</td></tr></table>'''

QWEN_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>qwen-max</td><td>0.02元/千tokens</td><td>0.06元/千tokens</td></tr>
<tr><td>qwen-plus</td><td>0.004元/千tokens</td><td>0.012元/千tokens</td></tr></table>'''

GLM_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>GLM-4-Plus</td><td>50元/百万tokens</td><td>50元/百万tokens</td></tr></table>'''

DOUBAO_HTML = '''<table><tr><th>模型</th><th>输入价格</th><th>输出价格</th></tr>
<tr><td>Doubao-pro-256k</td><td>5元/百万tokens</td><td>9元/百万tokens</td></tr></table>'''

MINIMAX_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>abab7-chat</td><td>10元/百万tokens</td><td>10元/百万tokens</td></tr></table>'''

ERNIE_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>ERNIE-4.5-8K</td><td>0.004元/千tokens</td><td>0.012元/千tokens</td></tr></table>'''

HUNYUAN_HTML = '''<table><tr><th>模型</th><th>输入价格</th><th>输出价格</th></tr>
<tr><td>hunyuan-pro</td><td>30元/百万tokens</td><td>100元/百万tokens</td></tr></table>'''

KIMI_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>moonshot-v1-128k</td><td>60元/百万tokens</td><td>60元/百万tokens</td></tr></table>'''

XIAOMI_HTML = '''<table><tr><th>模型</th><th>输入</th><th>输出</th></tr>
<tr><td>MiMo-7B</td><td>Free</td><td>Free</td></tr></table>'''


def test_deepseek_parse():
    results = DeepSeekCrawler._parse_html(DEEPSEEK_HTML)
    assert len(results) >= 1
    chat = next((r for r in results if "deepseek-chat" in r["name"].lower()), None)
    assert chat is not None
    assert chat["input_price"] == Decimal("1")
    assert chat["output_price"] == Decimal("4")
    assert chat["currency"] == "CNY"


def test_deepseek_parse_reasoner():
    results = DeepSeekCrawler._parse_html(DEEPSEEK_HTML)
    reasoner = next((r for r in results if "deepseek-reasoner" in r["name"].lower()), None)
    assert reasoner is not None
    assert reasoner["input_price"] == Decimal("4")
    assert reasoner["output_price"] == Decimal("16")


def test_qwen_parse():
    results = QwenCrawler._parse_html(QWEN_HTML)
    assert len(results) >= 1
    # 0.02元/千tokens = 20元/百万tokens
    qmax = next((r for r in results if "qwen-max" in r["name"].lower()), None)
    assert qmax is not None
    assert qmax["input_price"] == Decimal("20")
    assert qmax["output_price"] == Decimal("60")


def test_qwen_parse_plus():
    results = QwenCrawler._parse_html(QWEN_HTML)
    qplus = next((r for r in results if "qwen-plus" in r["name"].lower()), None)
    assert qplus is not None
    assert qplus["input_price"] == Decimal("4")
    assert qplus["output_price"] == Decimal("12")


def test_glm_parse():
    results = GLMCrawler._parse_html(GLM_HTML)
    assert len(results) >= 1
    glm = results[0]
    assert glm["input_price"] == Decimal("50")
    assert glm["output_price"] == Decimal("50")


def test_doubao_parse():
    results = DoubaoCrawler._parse_html(DOUBAO_HTML)
    assert len(results) >= 1
    doubao = results[0]
    assert doubao["input_price"] == Decimal("5")
    assert doubao["output_price"] == Decimal("9")


def test_minimax_parse():
    results = MiniMaxCrawler._parse_html(MINIMAX_HTML)
    assert len(results) >= 1
    abab = results[0]
    assert abab["input_price"] == Decimal("10")
    assert abab["output_price"] == Decimal("10")


def test_ernie_parse():
    results = ERNIECrawler._parse_html(ERNIE_HTML)
    assert len(results) >= 1
    # 0.004元/千tokens = 4元/百万tokens
    ernie = results[0]
    assert ernie["input_price"] == Decimal("4")
    assert ernie["output_price"] == Decimal("12")


def test_hunyuan_parse():
    results = HunyuanCrawler._parse_html(HUNYUAN_HTML)
    assert len(results) >= 1
    hy = results[0]
    assert hy["input_price"] == Decimal("30")
    assert hy["output_price"] == Decimal("100")


def test_kimi_parse():
    results = KimiCrawler._parse_html(KIMI_HTML)
    assert len(results) >= 1
    kimi = results[0]
    assert kimi["input_price"] == Decimal("60")
    assert kimi["output_price"] == Decimal("60")


def test_xiaomi_parse():
    results = XiaomiCrawler._parse_html(XIAOMI_HTML)
    assert len(results) >= 1
    # Free model should have price 0
    mimo = results[0]
    assert mimo["input_price"] == Decimal("0")
    assert mimo["output_price"] == Decimal("0")
