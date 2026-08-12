"""Auth Service FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.conf import Config
from src.database import async_session_maker, engine
from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.infrastructure.cache.config_email_blocklist_checker import (
    ConfigEmailBlocklistChecker,
)
from src.infrastructure.cache.in_memory_session_repository import (
    InMemorySessionRepository,
)
from src.infrastructure.cache.in_memory_verification_token_repository import (
    InMemoryVerificationTokenRepository,
)
from src.infrastructure.cache.redis_email_blocklist_checker import (
    RedisEmailBlocklistChecker,
)
from src.infrastructure.cache.redis_session_repository import RedisSessionRepository
from src.infrastructure.cache.redis_verification_token_repository import (
    RedisVerificationTokenRepository,
)
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.messaging.rabbitmq_event_publisher import (
    RabbitMQEventPublisher,
)
from src.infrastructure.persistence.models import Base
from src.presentation.api.v1 import api_v1_router
from src.redis_client import create_redis_client


def _build_event_publisher() -> EventPublisher:
    if Config.RABBITMQ_ENABLED:
        return RabbitMQEventPublisher(
            url=Config.RABBITMQ_URL,
            exchange_name=Config.RABBITMQ_EXCHANGE,
        )
    return NoOpEventPublisher()


def _build_session_repository(redis_client) -> SessionRepository:
    if Config.REDIS_ENABLED and redis_client is not None:
        return RedisSessionRepository(redis_client)
    return InMemorySessionRepository()


def _build_verification_token_repository(redis_client) -> VerificationTokenRepository:
    if Config.REDIS_ENABLED and redis_client is not None:
        return RedisVerificationTokenRepository(redis_client)
    return InMemoryVerificationTokenRepository()


def _build_email_blocklist(redis_client) -> EmailBlocklistChecker:
    if Config.REDIS_ENABLED and redis_client is not None:
        return RedisEmailBlocklistChecker(redis_client)
    return ConfigEmailBlocklistChecker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = app.state.event_publisher
    if isinstance(publisher, RabbitMQEventPublisher):
        await publisher.connect()

    yield

    if isinstance(publisher, RabbitMQEventPublisher):
        await publisher.close()
    redis_client = getattr(app.state, "redis_client", None)
    if redis_client is not None:
        await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="Auth Service",
    description="Authentication and session management for Cap.",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.engine = engine
app.state.session_factory = async_session_maker
app.state.event_publisher = _build_event_publisher()

_redis = create_redis_client() if Config.REDIS_ENABLED else None
app.state.redis_client = _redis
app.state.session_repository = _build_session_repository(_redis)
app.state.verification_token_repository = _build_verification_token_repository(_redis)
app.state.email_blocklist = _build_email_blocklist(_redis)

app.include_router(api_v1_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": Config.APP_NAME}
