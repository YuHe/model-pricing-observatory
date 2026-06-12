from __future__ import annotations
from datetime import date, timezone, datetime
from decimal import Decimal
from typing import Optional
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import Provider, Model, ModelCapability, PriceSnapshot, ExchangeRate
from app.crawlers.base import BaseCrawler

API_URL = "https://openrouter.ai/api/v1/models"


class OpenRouterCrawler(BaseCrawler):
    source = "openrouter"

    async def crawl(self, db: AsyncSession) -> int:
        # Get or create OpenRouter as channel provider
        result = await db.execute(select(Provider).where(Provider.name == "OpenRouter"))
        provider = result.scalar_one_or_none()
        if not provider:
            provider = Provider(name="OpenRouter", type="channel", country="US", official_url="https://openrouter.ai")
            db.add(provider)
            await db.commit()
            await db.refresh(provider)

        # Get today's exchange rate
        today = date.today()
        rate_result = await db.execute(select(ExchangeRate).where(ExchangeRate.date == today))
        rate_row = rate_result.scalar_one_or_none()
        exchange_rate = Decimal(str(rate_row.usd_cny)) if rate_row else Decimal("7.2")

        # Fetch models
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            data = resp.json()

        models_data = data.get("data", [])
        count = 0

        for item in models_data:
            model_id_str = item.get("id", "")
            pricing = item.get("pricing", {})
            if not pricing:
                continue

            prompt_price = pricing.get("prompt")
            completion_price = pricing.get("completion")
            if prompt_price is None and completion_price is None:
                continue

            # Parse prices (OpenRouter returns $/token, convert to $/M tokens)
            input_price = Decimal(str(prompt_price)) * 1_000_000 if prompt_price else None
            output_price = Decimal(str(completion_price)) * 1_000_000 if completion_price else None

            # Upsert model
            name = model_id_str
            stmt = insert(Model).values(
                provider_id=provider.id, name=name,
                family=self._extract_family(model_id_str),
                status="active"
            ).on_conflict_do_nothing(constraint="model_provider_id_name_key")
            await db.execute(stmt)
            await db.flush()

            # Get model
            model_result = await db.execute(
                select(Model).where(Model.provider_id == provider.id, Model.name == name)
            )
            model = model_result.scalar_one_or_none()
            if not model:
                continue

            # Upsert capability
            context_length = item.get("context_length")
            top_provider = item.get("top_provider", {})
            max_output = top_provider.get("max_completion_tokens") if top_provider else None

            stmt = insert(ModelCapability).values(
                model_id=model.id,
                context_window=context_length,
                max_output_tokens=max_output,
            ).on_conflict_do_update(
                index_elements=["model_id"],
                set_={"context_window": context_length, "max_output_tokens": max_output}
            )
            await db.execute(stmt)

            # Upsert price snapshot
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
                set_={
                    "input_price_per_m": input_price,
                    "output_price_per_m": output_price,
                    "input_price_cny": input_cny,
                    "output_price_cny": output_cny,
                    "exchange_rate": exchange_rate,
                }
            )
            await db.execute(stmt)
            count += 1

        await db.commit()
        return count

    @staticmethod
    def _extract_family(model_id: str) -> Optional[str]:
        parts = model_id.split("/")
        if len(parts) >= 2:
            return parts[1].split("-")[0].capitalize()
        return None
