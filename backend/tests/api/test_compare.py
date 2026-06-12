from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_compare_no_ids(client):
    response = await client.get("/api/v1/compare")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_compare_too_many_ids(client):
    ids = ",".join(["00000000-0000-0000-0000-000000000000"] * 11)
    response = await client.get(f"/api/v1/compare?ids={ids}")
    assert response.status_code == 400
