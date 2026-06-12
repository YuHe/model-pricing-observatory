from __future__ import annotations
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import JSON, event as sa_event
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app

# Patch JSONB columns to use JSON for SQLite compatibility
from app.models.models import SubscriptionPlan
SubscriptionPlan.__table__.c.features.type = JSON()

test_engine = create_async_engine("sqlite+aiosqlite://", echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True, scope="session")
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
