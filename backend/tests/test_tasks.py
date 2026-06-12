from __future__ import annotations
import pytest
from app.tasks.celery_app import celery_app
from app.tasks.sync import run_daily_sync


def test_celery_app_configured():
    assert celery_app.main == "pricing"
    assert "daily-sync" in celery_app.conf.beat_schedule


def test_daily_sync_task_registered():
    assert "app.tasks.sync.run_daily_sync" in celery_app.tasks
