from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from app.database import get_db
from app.models.models import PriceSnapshot, Model

router = APIRouter(prefix="/api/v1", tags=["price_changes"])


@router.get("/price-changes")
async def list_price_changes(
    direction: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    try:
        today = date.today()
        yesterday = today - timedelta(days=1)

        today_sub = select(PriceSnapshot.model_id, PriceSnapshot.input_price_cny.label("today_price")).where(PriceSnapshot.date == today).subquery()
        yesterday_sub = select(PriceSnapshot.model_id, PriceSnapshot.input_price_cny.label("yesterday_price")).where(PriceSnapshot.date == yesterday).subquery()

        stmt = select(
            Model.id, Model.name,
            today_sub.c.today_price,
            yesterday_sub.c.yesterday_price,
        ).join(today_sub, Model.id == today_sub.c.model_id).join(yesterday_sub, Model.id == yesterday_sub.c.model_id).where(
            and_(today_sub.c.today_price.isnot(None), yesterday_sub.c.yesterday_price.isnot(None), yesterday_sub.c.yesterday_price != 0)
        )

        if direction == "up":
            stmt = stmt.where(today_sub.c.today_price > yesterday_sub.c.yesterday_price)
        elif direction == "down":
            stmt = stmt.where(today_sub.c.today_price < yesterday_sub.c.yesterday_price)

        stmt = stmt.limit(limit)
        result = await db.execute(stmt)
        rows = result.all()
        return [{"model_id": str(r[0]), "name": r[1], "today_price": float(r[2]) if r[2] else None, "yesterday_price": float(r[3]) if r[3] else None, "change_percent": round(float((r[2] - r[3]) / r[3] * 100), 2) if r[2] and r[3] else None} for r in rows]
    except Exception:
        return []
