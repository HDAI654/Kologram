"""GraphQL / FastAPI dependency wiring for Market Service presentation."""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    """Resolve the application session factory from app state."""
    return request.app.state.session_factory


def get_event_publisher(request: Request) -> EventPublisher:
    """Resolve the configured event publisher from app state."""
    return request.app.state.event_publisher


def build_graphql_context(request: Request) -> dict:
    """
    Build Strawberry GraphQL context.

    Context keys:
      - request: FastAPI Request
      - uow_factory: zero-arg callable that returns a fresh UnitOfWork
      - event_publisher: EventPublisher adapter (NoOp or RabbitMQ)
    """
    session_factory = get_session_factory(request)

    def uow_factory() -> UnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory)

    return {
        "request": request,
        "uow_factory": uow_factory,
        "event_publisher": get_event_publisher(request),
    }
