"""Shared fixtures for application unit tests."""

import pytest

from src.domain.entities.category import Category
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER_ID = "550e8400-e29b-41d4-a716-446655440000"
OTHER_SELLER_ID = "550e8400-e29b-41d4-a716-446655440099"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
def events() -> NoOpEventPublisher:
    return NoOpEventPublisher()


@pytest.fixture
async def active_category(uow: InMemoryUnitOfWork) -> Category:
    category = Category.create(name="Electronics")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    return category
