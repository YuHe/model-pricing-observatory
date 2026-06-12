from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_providers_list(client):
    response = await client.get("/api/v1/providers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_providers_filter_by_type(client):
    response = await client.get("/api/v1/providers?type=official")
    assert response.status_code == 200
