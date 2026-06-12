from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import Provider, Model, PriceSnapshot

router = APIRouter(prefix="/api/v1", tags=["channels"])


@router.get("/channels")
async def list_channels(db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Provider, func.count(func.distinct(PriceSnapshot.model_id)).label("model_count")).outerjoin(
            PriceSnapshot, PriceSnapshot.channel_id == Provider.id
        ).where(Provider.type == "channel").group_by(Provider.id)
        result = await db.execute(stmt)
        rows = result.all()
        return [{"id": str(r[0].id), "name": r[0].name, "country": r[0].country, "model_count": r[1]} for r in rows]
    except Exception:
        return []


@router.get("/channels/{channel_id}/prices")
async def get_channel_prices(channel_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(PriceSnapshot).where(PriceSnapshot.channel_id == channel_id).order_by(PriceSnapshot.date.desc())
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [{"id": str(r.id), "date": str(r.date), "model_id": str(r.model_id), "input_price_cny": float(r.input_price_cny) if r.input_price_cny else None, "output_price_cny": float(r.output_price_cny) if r.output_price_cny else None} for r in rows]
    except Exception:
        return []
