from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import Provider, Model, PriceSnapshot, ExchangeRate
from app.crawlers.base import BaseCrawler
from app.crawlers.playwright_base import crawl_with_playwright

PRICING_URL = "https://www.huaweicloud.com/pricing/pangu"


class HuaweiCloudCrawler(BaseCrawler):
    source = "huaweicloud"

    async def crawl(self, db: AsyncSession) -> int:
        result = await db.execute(select(Provider).where(Provider.name == "华为云"))
        provider = result.scalar_one_or_none()
        if not provider:
            provider = Provider(name="华为云", type="channel", country="CN", official_url="https://www.huaweicloud.com")
            db.add(provider)
            await db.commit()
            await db.refresh(provider)

        today = date.today()
        rate_result = await db.execute(select(ExchangeRate).where(ExchangeRate.date == today))
        rate_row = rate_result.scalar_one_or_none()
        exchange_rate = Decimal(str(rate_row.usd_cny)) if rate_row else Decimal("7.2")

        html = await crawl_with_playwright(PRICING_URL, "table, .pricing", lambda x: x)
        models_data = self._parse_response(html)
        count = 0

        for item in models_data:
            stmt = insert(Model).values(
                provider_id=provider.id, name=item["name"],
                family=item.get("family"), status="active"
            ).on_conflict_do_nothing(constraint="model_provider_id_name_key")
            await db.execute(stmt)
            await db.flush()

            model_result = await db.execute(
                select(Model).where(Model.provider_id == provider.id, Model.name == item["name"])
            )
            model = model_result.scalar_one_or_none()
            if not model:
                continue

            input_price = item["input_price"]
            output_price = item["output_price"]
            input_usd = input_price / exchange_rate if input_price else None
            output_usd = output_price / exchange_rate if output_price else None

            stmt = insert(PriceSnapshot).values(
                date=today, model_id=model.id, channel_id=provider.id,
                currency="CNY",
                input_price_per_m=input_usd, output_price_per_m=output_usd,
                input_price_cny=input_price, output_price_cny=output_price,
                exchange_rate=exchange_rate,
            ).on_conflict_do_update(
                index_elements=["date", "model_id", "channel_id"],
                set_={"input_price_per_m": input_usd, "output_price_per_m": output_usd,
                       "input_price_cny": input_price, "output_price_cny": output_price, "exchange_rate": exchange_rate}
            )
            await db.execute(stmt)
            count += 1

        await db.commit()
        return count

    @staticmethod
    def _parse_response(html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        import re
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    name = cells[0].get_text(strip=True)
                    input_text = cells[1].get_text(strip=True)
                    output_text = cells[2].get_text(strip=True)
                    input_match = re.search(r"([\d.]+)", input_text)
                    output_match = re.search(r"([\d.]+)", output_text)
                    if name and input_match:
                        results.append({
                            "name": name,
                            "family": None,
                            "input_price": Decimal(input_match.group(1)),
                            "output_price": Decimal(output_match.group(1)) if output_match else None,
                        })
        return results
