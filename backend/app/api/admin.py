from __future__ import annotations
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.api.deps import require_admin
from app.models.models import CrawlJob, AlertConfig, AlertLog

router = APIRouter(prefix="/api/v1/admin", tags=["admin"], dependencies=[Depends(require_admin)])


class AlertCreate(BaseModel):
    type: str
    endpoint: str
    enabled: bool = True


class AlertUpdate(BaseModel):
    type: Optional[str] = None
    endpoint: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("/jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CrawlJob).order_by(CrawlJob.created_at.desc()))
        jobs = result.scalars().all()
        return [{"id": str(j.id), "source": j.source, "status": j.status, "started_at": str(j.started_at) if j.started_at else None, "finished_at": str(j.finished_at) if j.finished_at else None, "models_synced": j.models_synced, "error_message": j.error_message} for j in jobs]
    except Exception:
        return []


@router.get("/jobs/{job_id}")
async def get_job(job_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(CrawlJob).where(CrawlJob.id == job_id))
        j = result.scalar_one_or_none()
        if not j:
            raise HTTPException(status_code=404, detail="Job not found")
        return {"id": str(j.id), "source": j.source, "status": j.status, "started_at": str(j.started_at) if j.started_at else None, "finished_at": str(j.finished_at) if j.finished_at else None, "models_synced": j.models_synced, "error_message": j.error_message, "stack_trace": j.stack_trace, "retry_count": j.retry_count}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found")


@router.post("/jobs/{source}/retry")
async def retry_job(source: str, db: AsyncSession = Depends(get_db)):
    try:
        job = CrawlJob(source=source, status="pending")
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return {"id": str(job.id), "source": source, "status": "pending"}
    except Exception:
        return {"error": "Failed to create retry job"}


@router.get("/alerts")
async def list_alerts(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AlertConfig))
        alerts = result.scalars().all()
        return [{"id": str(a.id), "type": a.type, "endpoint": a.endpoint, "enabled": a.enabled} for a in alerts]
    except Exception:
        return []


@router.post("/alerts")
async def create_alert(body: AlertCreate, db: AsyncSession = Depends(get_db)):
    try:
        alert = AlertConfig(type=body.type, endpoint=body.endpoint, enabled=body.enabled)
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return {"id": str(alert.id), "type": alert.type, "endpoint": alert.endpoint, "enabled": alert.enabled}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create alert")


@router.put("/alerts/{alert_id}")
async def update_alert(alert_id: UUID, body: AlertUpdate, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AlertConfig).where(AlertConfig.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        if body.type is not None:
            alert.type = body.type
        if body.endpoint is not None:
            alert.endpoint = body.endpoint
        if body.enabled is not None:
            alert.enabled = body.enabled
        await db.commit()
        return {"id": str(alert.id), "type": alert.type, "endpoint": alert.endpoint, "enabled": alert.enabled}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update alert")


@router.delete("/alerts/{alert_id}")
async def delete_alert(alert_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AlertConfig).where(AlertConfig.id == alert_id))
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        await db.delete(alert)
        await db.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete alert")


@router.get("/alert-logs")
async def list_alert_logs(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(AlertLog).order_by(AlertLog.sent_at.desc()))
        logs = result.scalars().all()
        return [{"id": str(l.id), "alert_config_id": str(l.alert_config_id) if l.alert_config_id else None, "job_id": str(l.job_id) if l.job_id else None, "sent_at": str(l.sent_at), "status": l.status} for l in logs]
    except Exception:
        return []
