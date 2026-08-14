"""E2E fixtures — full FastAPI Auth Service stack (in-memory infra)."""

from __future__ import annotations

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("RABBITMQ_ENABLED", "false")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("BLOCKED_EMAILS", "")
os.environ.setdefault("BLOCKED_EMAIL_DOMAINS", "")


@pytest_asyncio.fixture
async def client():
    """HTTP client bound to the Auth Service ASGI app with a clean schema."""
    from src.app import app
    from src.database import engine as app_engine
    from src.infrastructure.persistence.models import Base

    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    token_repo = app.state.verification_token_repository
    if hasattr(token_repo, "_store"):
        token_repo._store.clear()
    session_repo = app.state.session_repository
    if hasattr(session_repo, "_by_id"):
        session_repo._by_id.clear()
    if hasattr(session_repo, "_by_user"):
        session_repo._by_user.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def app_instance(client: AsyncClient):
    from src.app import app

    return app
