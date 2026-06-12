from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.redis_client import redis_client
from app.api import models, providers, channels, plans, compare, stats, price_changes, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    await redis_client.aclose()


app = FastAPI(title="Model Pricing Observatory", lifespan=lifespan)

app.include_router(models.router)
app.include_router(providers.router)
app.include_router(channels.router)
app.include_router(plans.router)
app.include_router(compare.router)
app.include_router(stats.router)
app.include_router(price_changes.router)
app.include_router(admin.router)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
