from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_stats(client):
    response = await client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "provider_count" in data
    assert "model_count" in data
