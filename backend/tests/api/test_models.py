from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_models_list(client):
    response = await client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


@pytest.mark.asyncio
async def test_models_list_with_filters(client):
    response = await client.get("/api/v1/models?vision=true&sort_by=input_price_cny&sort_order=asc")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_models_detail_not_found(client):
    response = await client.get("/api/v1/models/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
