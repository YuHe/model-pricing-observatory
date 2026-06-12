from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_price_changes_default(client):
    response = await client.get("/api/v1/price-changes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_price_changes_with_direction(client):
    response = await client.get("/api/v1/price-changes?direction=down&limit=5")
    assert response.status_code == 200
