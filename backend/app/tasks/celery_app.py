from __future__ import annotations
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery("pricing", broker=settings.redis_url, backend=settings.redis_url)

celery_app.conf.beat_schedule = {
    "daily-sync": {
        "task": "app.tasks.sync.run_daily_sync",
        "schedule": crontab(hour=2, minute=0),
    },
}
celery_app.conf.timezone = "UTC"
