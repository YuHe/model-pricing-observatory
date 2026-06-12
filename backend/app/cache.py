from __future__ import annotations
import json
import hashlib
from typing import Optional, Any
from app.redis_client import redis_client

CACHE_TTLS = {
    "stats": 300,
    "models:list": 300,
    "models:detail": 600,
    "providers:list": 1800,
    "plans:list": 1800,
    "price_changes": 300,
}


async def get_cache(key: str) -> Optional[Any]:
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_cache(key: str, value: Any, ttl_key: str = "stats") -> None:
    ttl = CACHE_TTLS.get(ttl_key, 300)
    await redis_client.setex(key, ttl, json.dumps(value, default=str))


async def clear_all_cache() -> None:
    keys = await redis_client.keys("stats*")
    keys += await redis_client.keys("models:*")
    keys += await redis_client.keys("providers:*")
    keys += await redis_client.keys("plans:*")
    keys += await redis_client.keys("price_changes*")
    if keys:
        await redis_client.delete(*keys)


def cache_key_hash(prefix: str, params: dict) -> str:
    param_str = json.dumps(params, sort_keys=True, default=str)
    h = hashlib.md5(param_str.encode()).hexdigest()[:12]
    return f"{prefix}:{h}"
