from __future__ import annotations
import asyncio
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def run_daily_sync(self):
    """Execute all crawlers in sequence."""
    try:
        asyncio.run(_run_all_crawlers())
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=0)
def run_daily_sync_tracked(self):
    """Same as run_daily_sync but no retry — for manual trigger with progress tracking."""
    asyncio.run(_run_all_crawlers())


async def _run_all_crawlers():
    from app.crawlers.exchange_rate import ExchangeRateCrawler
    from app.crawlers.openrouter import OpenRouterCrawler
    from app.crawlers.openai import OpenAICrawler
    from app.crawlers.anthropic import AnthropicCrawler
    from app.crawlers.google import GoogleCrawler
    from app.crawlers.xai import XAICrawler
    from app.crawlers.mistral import MistralCrawler
    from app.crawlers.cohere import CohereCrawler
    from app.crawlers.deepseek import DeepSeekCrawler
    from app.crawlers.qwen import QwenCrawler
    from app.crawlers.glm import GLMCrawler
    from app.crawlers.doubao import DoubaoCrawler
    from app.crawlers.minimax import MiniMaxCrawler
    from app.crawlers.ernie import ERNIECrawler
    from app.crawlers.hunyuan import HunyuanCrawler
    from app.crawlers.kimi import KimiCrawler
    from app.crawlers.xiaomi import XiaomiCrawler
    from app.crawlers.siliconflow import SiliconFlowCrawler
    from app.crawlers.together import TogetherCrawler
    from app.crawlers.groq import GroqCrawler
    from app.crawlers.subscriptions import SubscriptionCrawler
    from app.cache import clear_all_cache
    from app.alerts import check_and_alert

    crawlers = [
        ExchangeRateCrawler(),
        OpenRouterCrawler(),
        OpenAICrawler(),
        AnthropicCrawler(),
        GoogleCrawler(),
        XAICrawler(),
        MistralCrawler(),
        CohereCrawler(),
        DeepSeekCrawler(),
        QwenCrawler(),
        GLMCrawler(),
        DoubaoCrawler(),
        MiniMaxCrawler(),
        ERNIECrawler(),
        HunyuanCrawler(),
        KimiCrawler(),
        XiaomiCrawler(),
        SiliconFlowCrawler(),
        TogetherCrawler(),
        GroqCrawler(),
        SubscriptionCrawler(),
    ]

    for crawler in crawlers:
        await crawler.run()

    await check_and_alert()
    await clear_all_cache()
