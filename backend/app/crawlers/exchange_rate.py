from __future__ import annotations
from datetime import date, timezone, datetime
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models import ExchangeRate
from app.crawlers.base import BaseCrawler

API_URL = "https://api.exchangerate-api.com/v4/latest/USD"


class ExchangeRateCrawler(BaseCrawler):
    source = "exchange_rate"

    async def crawl(self, db: AsyncSession) -> int:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(API_URL)
            resp.raise_for_status()
            data = resp.json()

        cny_rate = data["rates"]["CNY"]
        today = date.today()

        stmt = insert(ExchangeRate).values(
            date=today, usd_cny=cny_rate
        ).on_conflict_do_update(
            index_elements=["date"],
            set_={"usd_cny": cny_rate, "created_at": datetime.now(timezone.utc)}
        )
        await db.execute(stmt)
        await db.commit()
        return 1
