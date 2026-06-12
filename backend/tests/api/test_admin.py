from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_admin_jobs_requires_key(client):
    response = await client.get("/api/v1/admin/jobs")
    assert response.status_code == 422  # missing header


@pytest.mark.asyncio
async def test_admin_jobs_invalid_key(client):
    response = await client.get("/api/v1/admin/jobs", headers={"X-Admin-Key": "wrong"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_jobs_valid_key(client):
    response = await client.get("/api/v1/admin/jobs", headers={"X-Admin-Key": "change-me-in-production"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_admin_alerts_crud(client):
    headers = {"X-Admin-Key": "change-me-in-production"}
    # Create
    response = await client.post("/api/v1/admin/alerts", headers=headers, json={"type": "webhook", "endpoint": "https://example.com/hook"})
    assert response.status_code == 200
    alert_id = response.json()["id"]

    # List
    response = await client.get("/api/v1/admin/alerts", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # Delete
    response = await client.delete(f"/api/v1/admin/alerts/{alert_id}", headers=headers)
    assert response.status_code == 200
