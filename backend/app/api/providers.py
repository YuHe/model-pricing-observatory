from __future__ import annotations
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.models import Provider, Model

router = APIRouter(prefix="/api/v1", tags=["providers"])


@router.get("/providers")
async def list_providers(type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Provider)
        if type:
            stmt = stmt.where(Provider.type == type)
        result = await db.execute(stmt)
        providers = result.scalars().all()
        return [{"id": str(p.id), "name": p.name, "type": p.type, "country": p.country, "official_url": p.official_url, "logo_url": p.logo_url} for p in providers]
    except Exception:
        return []


@router.get("/providers/{provider_id}")
async def get_provider(provider_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Provider).options(selectinload(Provider.models)).where(Provider.id == provider_id)
        result = await db.execute(stmt)
        p = result.scalar_one_or_none()
        if not p:
            raise HTTPException(status_code=404, detail="Provider not found")
        return {
            "id": str(p.id), "name": p.name, "type": p.type, "country": p.country,
            "official_url": p.official_url, "logo_url": p.logo_url,
            "models": [{"id": str(m.id), "name": m.name, "family": m.family, "status": m.status} for m in p.models],
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Provider not found")
