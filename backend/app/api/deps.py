from __future__ import annotations
from fastapi import Header, HTTPException
from app.config import settings


async def require_admin(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin key")
