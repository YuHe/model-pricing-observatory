from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import Provider, Model, PriceSnapshot, SubscriptionPlan

router = APIRouter(prefix="/api/v1", tags=["stats"])


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    try:
        provider_count = (await db.execute(select(func.count()).select_from(Provider))).scalar() or 0
        model_count = (await db.execute(select(func.count()).select_from(Model))).scalar() or 0
        snapshot_count = (await db.execute(select(func.count()).select_from(PriceSnapshot))).scalar() or 0
        plan_count = (await db.execute(select(func.count()).select_from(SubscriptionPlan))).scalar() or 0
        return {"provider_count": provider_count, "model_count": model_count, "snapshot_count": snapshot_count, "plan_count": plan_count}
    except Exception:
        return {"provider_count": 0, "model_count": 0, "snapshot_count": 0, "plan_count": 0}
