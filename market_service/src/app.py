from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Callable
from strawberry.fastapi import GraphQLRouter
from src.conf import Config
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.presentation.dependencies import build_graphql_context
from src.presentation.graphql.schema import schema
from src.fake_dev_data import _seed_dev_categories, _seed_dev_listings


def _build_event_publisher() -> EventPublisher:
    if Config.RABBITMQ_ENABLED:
        from src.infrastructure.messaging.rabbitmq_event_publisher import (
            RabbitMQEventPublisher,
        )

        return RabbitMQEventPublisher(
            url=Config.RABBITMQ_URL,
            exchange_name=Config.RABBITMQ_EXCHANGE,
        )

    from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher

    return NoOpEventPublisher()


def _build_uow() -> Callable[[], UnitOfWork]:
    if Config.APP_ENV == "development":
        from src.infrastructure.persistence.in_memory_unit_of_work import (
            InMemoryUnitOfWork,
        )
        from src.domain.entities.category import Category
        from src.domain.entities.listing import Listing

        _dev_categories: dict[str, Category] = {}
        _dev_listings: dict[str, Listing] = {}
        _seed_dev_categories(_dev_categories)
        _seed_dev_listings(_dev_listings)

        return lambda: InMemoryUnitOfWork(
            listings=_dev_listings,
            categories=_dev_categories,
        )

    from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
    from src.database import async_session_maker

    return lambda: SQLAlchemyUnitOfWork(async_session_maker)


if Config.APP_ENV == "development":
    app = FastAPI(title="Kologram")
else:
    from src.infrastructure.messaging.rabbitmq_event_publisher import (
        RabbitMQEventPublisher,
    )
    from src.database import engine
    from src.infrastructure.persistence.models import Base

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

app.state.event_publisher = _build_event_publisher()
app.state.uow = _build_uow()

graphql_app = GraphQLRouter(
    schema,
    context_getter=build_graphql_context,
    graphql_ide="graphiql",
)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": Config.APP_NAME}
