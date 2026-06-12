from __future__ import annotations
import re
from datetime import date
from decimal import Decimal
from typing import List, Dict
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import SubscriptionPlan, SubscriptionSnapshot, ExchangeRate
from app.crawlers.base import BaseCrawler
from app.crawlers.playwright_base import crawl_with_playwright

SUBSCRIPTION_SOURCES = [
    {"provider": "Anthropic", "url": "https://claude.ai/pricing", "selector": ".pricing, [class*=price]"},
    {"provider": "Cursor", "url": "https://www.cursor.com/pricing", "selector": ".pricing, [class*=price]"},
    {"provider": "GitHub", "url": "https://github.com/features/copilot#pricing", "selector": ".pricing, [class*=price]"},
    {"provider": "Windsurf", "url": "https://windsurf.com/pricing", "selector": ".pricing, [class*=price]"},
    {"provider": "Augment", "url": "https://www.augmentcode.com/pricing", "selector": ".pricing, [class*=price]"},
    {"provider": "Devin", "url": "https://devin.ai/pricing", "selector": ".pricing, [class*=price]"},
]


class SubscriptionCrawler(BaseCrawler):
    source = "subscriptions"

    async def crawl(self, db: AsyncSession) -> int:
        today = date.today()
        rate_result = await db.execute(select(ExchangeRate).where(ExchangeRate.date == today))
        rate_row = rate_result.scalar_one_or_none()
        exchange_rate = Decimal(str(rate_row.usd_cny)) if rate_row else Decimal("7.2")

        count = 0
        for source in SUBSCRIPTION_SOURCES:
            try:
                html = await crawl_with_playwright(source["url"], source["selector"], lambda x: x)
                plans = self._parse_pricing_page(html, source["provider"])
                for plan in plans:
                    monthly_cny = plan["monthly_price"] * exchange_rate
                    stmt = insert(SubscriptionPlan).values(
                        provider=source["provider"],
                        plan_name=plan["plan_name"],
                        monthly_price=plan["monthly_price"],
                        currency="USD",
                        monthly_price_cny=monthly_cny,
                        features=plan.get("features"),
                        source_url=source["url"],
                    ).on_conflict_do_update(
                        constraint="subscription_plan_provider_plan_name_key",
                        set_={"monthly_price": plan["monthly_price"], "monthly_price_cny": monthly_cny}
                    )
                    await db.execute(stmt)

                    plan_result = await db.execute(
                        select(SubscriptionPlan).where(
                            SubscriptionPlan.provider == source["provider"],
                            SubscriptionPlan.plan_name == plan["plan_name"]
                        )
                    )
                    plan_obj = plan_result.scalar_one()

                    stmt = insert(SubscriptionSnapshot).values(
                        date=today, plan_id=plan_obj.id,
                        monthly_price=plan["monthly_price"],
                        monthly_price_cny=monthly_cny,
                        exchange_rate=exchange_rate,
                    ).on_conflict_do_nothing()
                    await db.execute(stmt)
                    count += 1
            except Exception:
                continue
        await db.commit()
        return count

    @staticmethod
    def _parse_pricing_page(html: str, provider: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        price_pattern = re.compile(r"\$(\d+(?:\.\d+)?)")
        for el in soup.find_all(string=price_pattern):
            match = price_pattern.search(el)
            if match:
                price = Decimal(match.group(1))
                parent = el.parent
                if parent:
                    plan_name = parent.get_text(strip=True).split("$")[0].strip() or f"{provider} Plan"
                    results.append({"plan_name": plan_name, "monthly_price": price, "features": None})
        return results
