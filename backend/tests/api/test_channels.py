from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_channels_list(client):
    response = await client.get("/api/v1/channels")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
