from __future__ import annotations
import traceback
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CrawlJob
from app.database import async_session


class BaseCrawler:
    source: str = ""

    async def run(self) -> None:
        async with async_session() as db:
            job = CrawlJob(source=self.source, status="running", started_at=datetime.now(timezone.utc))
            db.add(job)
            await db.commit()
            await db.refresh(job)
            try:
                count = await self.crawl(db)
                job.status = "success"
                job.models_synced = count
                job.finished_at = datetime.now(timezone.utc)
            except Exception as e:
                job.status = "failed"
                job.error_message = str(e)
                job.stack_trace = traceback.format_exc()
                job.finished_at = datetime.now(timezone.utc)
            await db.commit()

    async def crawl(self, db: AsyncSession) -> int:
        raise NotImplementedError
