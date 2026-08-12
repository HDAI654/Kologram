"""Market Service — FastAPI host with Strawberry GraphQL presentation."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from src.conf import Config
from src.database import async_session_maker, engine
from src.domain.ports.event_publisher import EventPublisher
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.messaging.rabbitmq_event_publisher import RabbitMQEventPublisher
from src.infrastructure.persistence.models import Base
from src.presentation.dependencies import build_graphql_context
from src.presentation.graphql.schema import schema


def _build_event_publisher() -> EventPublisher:
    if Config.RABBITMQ_ENABLED:
        return RabbitMQEventPublisher(
            url=Config.RABBITMQ_URL,
            exchange_name=Config.RABBITMQ_EXCHANGE,
        )
    return NoOpEventPublisher()


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
    await engine.dispose()


app = FastAPI(
    title="Market Service",
    description="GraphQL API for listings, categories and search (Cap marketplace).",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.engine = engine
app.state.session_factory = async_session_maker
app.state.event_publisher = _build_event_publisher()

graphql_app = GraphQLRouter(
    schema,
    context_getter=build_graphql_context,
    graphql_ide="graphiql",
)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": Config.APP_NAME}
