from __future__ import annotations
from app.tasks.celery_app import celery_app
from app.tasks.sync import run_daily_sync
