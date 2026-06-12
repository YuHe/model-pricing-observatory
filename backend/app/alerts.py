from __future__ import annotations
import json
from datetime import datetime, timezone
import httpx
import aiosmtplib
from email.mime.text import MIMEText
from sqlalchemy import select, func
from app.database import async_session
from app.models import CrawlJob, AlertConfig, AlertLog
from app.config import settings


async def check_and_alert() -> None:
    """Check for failed jobs and send alerts."""
    async with async_session() as db:
        result = await db.execute(
            select(CrawlJob)
            .where(CrawlJob.status == "failed")
            .order_by(CrawlJob.created_at.desc())
            .limit(20)
        )
        failed_jobs = result.scalars().all()

        if not failed_jobs:
            return

        configs_result = await db.execute(
            select(AlertConfig).where(AlertConfig.enabled == True)
        )
        configs = configs_result.scalars().all()

        for job in failed_jobs:
            for config in configs:
                try:
                    if config.type == "webhook":
                        await _send_webhook(config.endpoint, job)
                    elif config.type == "email":
                        await _send_email(config.endpoint, job)

                    log = AlertLog(
                        alert_config_id=config.id, job_id=job.id,
                        status="sent"
                    )
                except Exception as e:
                    log = AlertLog(
                        alert_config_id=config.id, job_id=job.id,
                        status="failed", error_message=str(e)
                    )
                db.add(log)
        await db.commit()


async def _send_webhook(url: str, job: CrawlJob) -> None:
    payload = {
        "source": job.source,
        "error": job.error_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "job_id": str(job.id),
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()


async def _send_email(to_addr: str, job: CrawlJob) -> None:
    if not settings.smtp_host:
        return
    msg = MIMEText(
        f"Crawler failed: {job.source}\nError: {job.error_message}\nTime: {job.finished_at}"
    )
    msg["Subject"] = f"[MPO Alert] Crawler failed: {job.source}"
    msg["From"] = settings.smtp_user
    msg["To"] = to_addr

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_pass,
        use_tls=True,
    )
