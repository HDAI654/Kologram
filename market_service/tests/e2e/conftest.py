"""E2E fixtures — full FastAPI + GraphQL stack."""

from __future__ import annotations

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Feature flags off for e2e (NoOp messaging, no external deps).
os.environ.setdefault("RABBITMQ_ENABLED", "false")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("APP_ENV", "test")


@pytest_asyncio.fixture
async def client():
    """HTTP client bound to the Market Service ASGI app with clean schema."""
    from src.app import app
    from src.database import engine as app_engine
    from src.infrastructure.persistence.models import Base

    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
