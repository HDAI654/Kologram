import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.get_listing import GetListingHandler, GetListingQuery
from src.application.publish_listing import PublishListingCommand, PublishListingHandler
from src.domain.entities.category import Category
from src.exceptions import ListingNotFoundError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.mark.asyncio
async def test_get_listing(uow: InMemoryUnitOfWork) -> None:
    category = Category.create(name="Gadgets")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    created = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="Wireless Mouse",
            description="Ergonomic",
            price_amount="29.99",
            quantity=5,
            location="Berlin",
        )
    )
    await PublishListingHandler(uow, NoOpEventPublisher()).handle(
        PublishListingCommand(listing_id=created.listing_id, seller_id=SELLER)
    )
    result = await GetListingHandler(uow).handle(
        GetListingQuery(listing_id=created.listing_id)
    )
    assert result.title == "Wireless Mouse"
    assert result.status == "ACTIVE"


@pytest.mark.asyncio
async def test_get_listing_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(ListingNotFoundError):
        await GetListingHandler(uow).handle(
            GetListingQuery(listing_id="550e8400-e29b-41d4-a716-446655440099")
        )
