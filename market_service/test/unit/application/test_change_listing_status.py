import pytest

from src.application.change_listing_status import (
    ChangeListingStatusCommand,
    ChangeListingStatusHandler,
)
from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.publish_listing import PublishListingCommand, PublishListingHandler
from src.domain.entities.category import Category
from src.exceptions import InvalidListingTransitionError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
async def active_listing_id(uow: InMemoryUnitOfWork) -> str:
    category = Category.create(name="StatusCat")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    created = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="Status Item XX",
            description="",
            price_amount="50",
            quantity=1,
            location="Madrid",
        )
    )
    await PublishListingHandler(uow, NoOpEventPublisher()).handle(
        PublishListingCommand(listing_id=created.listing_id, seller_id=SELLER)
    )
    return created.listing_id


@pytest.mark.asyncio
async def test_mark_sold(uow: InMemoryUnitOfWork, active_listing_id: str) -> None:
    result = await ChangeListingStatusHandler(uow, NoOpEventPublisher()).handle(
        ChangeListingStatusCommand(
            listing_id=active_listing_id,
            seller_id=SELLER,
            new_status="SOLD",
        )
    )
    assert result.status == "SOLD"


@pytest.mark.asyncio
async def test_invalid_transition(
    uow: InMemoryUnitOfWork, active_listing_id: str
) -> None:
    handler = ChangeListingStatusHandler(uow, NoOpEventPublisher())
    await handler.handle(
        ChangeListingStatusCommand(
            listing_id=active_listing_id, seller_id=SELLER, new_status="SOLD"
        )
    )
    with pytest.raises(InvalidListingTransitionError):
        await handler.handle(
            ChangeListingStatusCommand(
                listing_id=active_listing_id, seller_id=SELLER, new_status="ACTIVE"
            )
        )
