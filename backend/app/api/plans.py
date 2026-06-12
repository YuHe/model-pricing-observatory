from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.models import SubscriptionPlan, SubscriptionSnapshot

router = APIRouter(prefix="/api/v1", tags=["plans"])


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(SubscriptionPlan))
        plans = result.scalars().all()
        return [{"id": str(p.id), "provider": p.provider, "plan_name": p.plan_name, "monthly_price": float(p.monthly_price) if p.monthly_price else None, "currency": p.currency, "monthly_price_cny": float(p.monthly_price_cny) if p.monthly_price_cny else None, "features": p.features} for p in plans]
    except Exception:
        return []


@router.get("/plans/{plan_id}")
async def get_plan(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
        p = result.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=404, detail="Plan not found")
        return {"id": str(p.id), "provider": p.provider, "plan_name": p.plan_name, "monthly_price": float(p.monthly_price) if p.monthly_price else None, "annual_price": float(p.annual_price) if p.annual_price else None, "currency": p.currency, "monthly_price_cny": float(p.monthly_price_cny) if p.monthly_price_cny else None, "features": p.features, "source_url": p.source_url}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Plan not found")


@router.get("/plans/{plan_id}/history")
async def get_plan_history(plan_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(SubscriptionSnapshot).where(SubscriptionSnapshot.plan_id == plan_id).order_by(SubscriptionSnapshot.date)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [{"date": str(r.date), "monthly_price": float(r.monthly_price) if r.monthly_price else None, "monthly_price_cny": float(r.monthly_price_cny) if r.monthly_price_cny else None} for r in rows]
    except Exception:
        return []
