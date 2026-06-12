from __future__ import annotations
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import Provider, Model, PriceSnapshot, ExchangeRate
from app.crawlers.base import BaseCrawler

API_URL = "https://api.siliconflow.cn/v1/models"


class SiliconFlowCrawler(BaseCrawler):
    source = "siliconflow"

    async def crawl(self, db: AsyncSession) -> int:
        result = await db.execute(select(Provider).where(Provider.name == "SiliconFlow"))
        provider = result.scalar_one_or_none()
        if not provider:
            provider = Provider(name="SiliconFlow", type="channel", country="CN", official_url="https://siliconflow.cn")
            db.add(provider)
            await db.commit()
            await db.refresh(provider)

        today = date.today()
        rate_result = await db.execute(select(ExchangeRate).where(ExchangeRate.date == today))
        rate_row = rate_result.scalar_one_or_none()
        exchange_rate = Decimal(str(rate_row.usd_cny)) if rate_row else Decimal("7.2")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            data = resp.json()

        models_data = self._parse_response(data)
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
            input_cny = input_price * exchange_rate if input_price else None
            output_cny = output_price * exchange_rate if output_price else None

            stmt = insert(PriceSnapshot).values(
                date=today, model_id=model.id, channel_id=provider.id,
                currency="USD",
                input_price_per_m=input_price, output_price_per_m=output_price,
                input_price_cny=input_cny, output_price_cny=output_cny,
                exchange_rate=exchange_rate,
            ).on_conflict_do_update(
                index_elements=["date", "model_id", "channel_id"],
                set_={"input_price_per_m": input_price, "output_price_per_m": output_price,
                       "input_price_cny": input_cny, "output_price_cny": output_cny, "exchange_rate": exchange_rate}
            )
            await db.execute(stmt)
            count += 1

        await db.commit()
        return count

    @staticmethod
    def _parse_response(data: dict) -> List[Dict]:
        results = []
        for item in data.get("data", []):
            pricing = item.get("pricing", {})
            if not pricing:
                continue
            input_raw = pricing.get("input")
            output_raw = pricing.get("output")
            if input_raw is None and output_raw is None:
                continue
            input_price = Decimal(str(input_raw)) * 1_000_000 if input_raw else None
            output_price = Decimal(str(output_raw)) * 1_000_000 if output_raw else None
            model_id = item.get("id", "")
            results.append({
                "name": model_id,
                "family": SiliconFlowCrawler._extract_family(model_id),
                "input_price": input_price,
                "output_price": output_price,
            })
        return results

    @staticmethod
    def _extract_family(model_id: str) -> Optional[str]:
        parts = model_id.split("/")
        if len(parts) >= 2:
            return parts[0]
        return None
