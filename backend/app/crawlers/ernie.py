from __future__ import annotations
import re
from datetime import date
from decimal import Decimal
from typing import List, Dict
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import Provider, Model, PriceSnapshot
from app.crawlers.base import BaseCrawler
from app.crawlers.playwright_base import crawl_with_playwright

PRICE_RE = re.compile(r"([\d.]+)元/(百万|千)tokens")


def _parse_price(text: str) -> Decimal:
    if "free" in text.lower():
        return Decimal("0")
    m = PRICE_RE.search(text)
    if not m:
        return Decimal("0")
    val = Decimal(m.group(1))
    if m.group(2) == "千":
        val *= 1000
    return val


class ERNIECrawler(BaseCrawler):
    source = "ernie"
    URL = "https://cloud.baidu.com/doc/WENXINWORKSHOP/s/hlrk4akp7"
    WAIT_SELECTOR = "table"
    PROVIDER_NAME = "ERNIE"
    COUNTRY = "CN"
    CURRENCY = "CNY"

    async def crawl(self, db: AsyncSession) -> int:
        html = await crawl_with_playwright(self.URL, self.WAIT_SELECTOR, lambda x: x)
        models_data = self._parse_html(html)
        result = await db.execute(select(Provider).where(Provider.name == self.PROVIDER_NAME))
        provider = result.scalar_one_or_none()
        if not provider:
            provider = Provider(name=self.PROVIDER_NAME, type="official", country=self.COUNTRY, official_url=self.URL)
            db.add(provider)
            await db.commit()
            await db.refresh(provider)
        today = date.today()
        count = 0
        for item in models_data:
            stmt = insert(Model).values(
                provider_id=provider.id, name=item["name"], status="active"
            ).on_conflict_do_nothing(constraint="model_provider_id_name_key")
            await db.execute(stmt)
            await db.flush()
            model_result = await db.execute(
                select(Model).where(Model.provider_id == provider.id, Model.name == item["name"])
            )
            model = model_result.scalar_one_or_none()
            if not model:
                continue
            stmt = insert(PriceSnapshot).values(
                date=today, model_id=model.id, channel_id=provider.id,
                currency=self.CURRENCY,
                input_price_per_m=item["input_price"], output_price_per_m=item["output_price"],
                input_price_cny=item["input_price"], output_price_cny=item["output_price"],
                exchange_rate=Decimal("1"),
            ).on_conflict_do_update(
                index_elements=["date", "model_id", "channel_id"],
                set_={"input_price_per_m": item["input_price"], "output_price_per_m": item["output_price"],
                       "input_price_cny": item["input_price"], "output_price_cny": item["output_price"],
                       "exchange_rate": Decimal("1")}
            )
            await db.execute(stmt)
            count += 1
        await db.commit()
        return count

    @staticmethod
    def _parse_html(html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if len(cells) < 3:
                    continue
                name = cells[0].get_text(strip=True)
                input_price = _parse_price(cells[1].get_text(strip=True))
                output_price = _parse_price(cells[2].get_text(strip=True))
                results.append({"name": name, "input_price": input_price, "output_price": output_price, "currency": "CNY"})
        return results
