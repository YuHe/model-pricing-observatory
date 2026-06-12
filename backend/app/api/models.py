from __future__ import annotations
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, desc, asc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.models import Model, ModelCapability, PriceSnapshot, Provider

router = APIRouter(prefix="/api/v1", tags=["models"])


@router.get("/models")
async def list_models(
    provider: Optional[UUID] = None,
    family: Optional[str] = None,
    channel: Optional[UUID] = None,
    vision: Optional[bool] = None,
    reasoning: Optional[bool] = None,
    tool_calling: Optional[bool] = None,
    structured_output: Optional[bool] = None,
    batch_api: Optional[bool] = None,
    fine_tuning: Optional[bool] = None,
    prompt_caching: Optional[bool] = None,
    min_context: Optional[int] = None,
    max_context: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    try:
        # Build base query
        stmt = select(Model).outerjoin(ModelCapability).outerjoin(
            PriceSnapshot, and_(
                PriceSnapshot.model_id == Model.id,
                PriceSnapshot.date == select(func.max(PriceSnapshot.date)).where(PriceSnapshot.model_id == Model.id).correlate(Model).scalar_subquery()
            )
        )

        filters = []
        if provider:
            filters.append(Model.provider_id == provider)
        if family:
            filters.append(Model.family == family)
        if channel:
            filters.append(PriceSnapshot.channel_id == channel)
        if search:
            filters.append(Model.name.ilike(f"%{search}%"))
        if vision is not None:
            filters.append(ModelCapability.vision == vision)
        if reasoning is not None:
            filters.append(ModelCapability.reasoning == reasoning)
        if tool_calling is not None:
            filters.append(ModelCapability.tool_calling == tool_calling)
        if structured_output is not None:
            filters.append(ModelCapability.structured_output == structured_output)
        if batch_api is not None:
            filters.append(ModelCapability.batch_api == batch_api)
        if fine_tuning is not None:
            filters.append(ModelCapability.fine_tuning == fine_tuning)
        if prompt_caching is not None:
            filters.append(ModelCapability.prompt_caching == prompt_caching)
        if min_context is not None:
            filters.append(ModelCapability.context_window >= min_context)
        if max_context is not None:
            filters.append(ModelCapability.context_window <= max_context)
        if min_price is not None:
            filters.append(PriceSnapshot.input_price_cny >= min_price)
        if max_price is not None:
            filters.append(PriceSnapshot.input_price_cny <= max_price)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await db.execute(count_stmt)).scalar() or 0

        # Sort
        sort_col = Model.created_at
        if sort_by == "input_price_cny":
            sort_col = PriceSnapshot.input_price_cny
        elif sort_by == "output_price_cny":
            sort_col = PriceSnapshot.output_price_cny
        elif sort_by == "name":
            sort_col = Model.name
        elif sort_by == "context_window":
            sort_col = ModelCapability.context_window

        stmt = stmt.order_by(desc(sort_col) if sort_order == "desc" else asc(sort_col))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        models = result.scalars().unique().all()

        items = []
        for m in models:
            item = {"id": str(m.id), "name": m.name, "family": m.family, "provider_id": str(m.provider_id), "status": m.status}
            items.append(item)

        return {"items": items, "total": total, "page": page, "page_size": page_size}
    except Exception:
        return {"items": [], "total": 0, "page": page, "page_size": page_size}


@router.get("/models/{model_id}")
async def get_model(model_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(Model).options(selectinload(Model.capability), selectinload(Model.aliases)).where(Model.id == model_id)
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return {
            "id": str(model.id), "name": model.name, "family": model.family,
            "provider_id": str(model.provider_id), "status": model.status,
            "description": model.description, "release_date": str(model.release_date) if model.release_date else None,
            "capability": {
                "context_window": model.capability.context_window if model.capability else None,
                "vision": model.capability.vision if model.capability else False,
                "reasoning": model.capability.reasoning if model.capability else False,
            } if model.capability else None,
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Model not found")


@router.get("/models/{model_id}/history")
async def get_model_history(model_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        stmt = select(PriceSnapshot).where(PriceSnapshot.model_id == model_id).order_by(PriceSnapshot.date)
        result = await db.execute(stmt)
        rows = result.scalars().all()
        return [{"date": str(r.date), "input_price_cny": float(r.input_price_cny) if r.input_price_cny else None, "output_price_cny": float(r.output_price_cny) if r.output_price_cny else None, "channel_id": str(r.channel_id)} for r in rows]
    except Exception:
        return []
