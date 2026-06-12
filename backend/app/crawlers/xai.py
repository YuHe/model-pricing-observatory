from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from typing import List, Dict

from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.models import Provider, Model, ModelCapability, PriceSnapshot, ExchangeRate
from app.crawlers.base import BaseCrawler

PRICE_RE = re.compile(r"\$?([\d,]+\.?\d*)")


class XAICrawler(BaseCrawler):
    source = "xai"
    URL = "https://docs.x.ai/docs/models#models-and-pricing"
    WAIT_SELECTOR = "table"

    async def crawl(self, db: AsyncSession) -> int:
        from app.crawlers.playwright_base import crawl_with_playwright
        html = await crawl_with_playwright(self.URL, self.WAIT_SELECTOR, lambda x: x)
        models_data = self._parse_html(html)
        if not models_data:
            return 0

        result = await db.execute(select(Provider).where(Provider.name == "xAI"))
        provider = result.scalar_one_or_none()
        if not provider:
            provider = Provider(name="xAI", type="official", country="US", official_url=self.URL)
            db.add(provider)
            await db.commit()
            await db.refresh(provider)

        today = date.today()
        rate_row = (await db.execute(select(ExchangeRate).where(ExchangeRate.date == today))).scalar_one_or_none()
        ex_rate = Decimal(str(rate_row.usd_cny)) if rate_row else Decimal("7.2")

        count = 0
        for item in models_data:
            name = item["name"]
            inp = item["input_price"]
            out = item["output_price"]

            stmt = insert(Model).values(provider_id=provider.id, name=name, status="active").on_conflict_do_nothing(constraint="model_provider_id_name_key")
            await db.execute(stmt)
            await db.flush()

            model = (await db.execute(select(Model).where(Model.provider_id == provider.id, Model.name == name))).scalar_one_or_none()
            if not model:
                continue

            inp_cny = inp * ex_rate if inp else None
            out_cny = out * ex_rate if out else None

            stmt = insert(PriceSnapshot).values(
                date=today, model_id=model.id, channel_id=provider.id,
                currency="USD", input_price_per_m=inp, output_price_per_m=out,
                input_price_cny=inp_cny, output_price_cny=out_cny, exchange_rate=ex_rate,
            ).on_conflict_do_update(
                index_elements=["date", "model_id", "channel_id"],
                set_={"input_price_per_m": inp, "output_price_per_m": out, "input_price_cny": inp_cny, "output_price_cny": out_cny, "exchange_rate": ex_rate},
            )
            await db.execute(stmt)
            count += 1

        await db.commit()
        return count

    @staticmethod
    def _parse_html(html: str) -> List[Dict]:
        soup = BeautifulSoup(html, "html.parser")
        results: List[Dict] = []
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:
                cols = row.find_all(["td", "th"])
                if len(cols) < 3:
                    continue
                name = cols[0].get_text(strip=True).lower()
                inp_match = PRICE_RE.search(cols[1].get_text(strip=True))
                out_match = PRICE_RE.search(cols[2].get_text(strip=True))
                if inp_match and out_match:
                    results.append({
                        "name": name,
                        "input_price": Decimal(inp_match.group(1).replace(",", "")),
                        "output_price": Decimal(out_match.group(1).replace(",", "")),
                    })
        return results
