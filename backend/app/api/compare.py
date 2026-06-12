from __future__ import annotations
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.models import Model, ModelCapability, PriceSnapshot

router = APIRouter(prefix="/api/v1", tags=["compare"])


@router.get("/compare")
async def compare_models(ids: Optional[str] = Query(None), db: AsyncSession = Depends(get_db)):
    if not ids:
        return []
    id_list = [i.strip() for i in ids.split(",") if i.strip()]
    if len(id_list) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 models")
    try:
        uuids = [UUID(i) for i in id_list]
        stmt = select(Model).options(selectinload(Model.capability)).where(Model.id.in_(uuids))
        result = await db.execute(stmt)
        models = result.scalars().all()
        items = []
        for m in models:
            item = {"id": str(m.id), "name": m.name, "family": m.family, "provider_id": str(m.provider_id)}
            if m.capability:
                item["capability"] = {"context_window": m.capability.context_window, "vision": m.capability.vision, "reasoning": m.capability.reasoning}
            items.append(item)
        return items
    except HTTPException:
        raise
    except Exception:
        return []
