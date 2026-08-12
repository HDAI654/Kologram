import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.publish_listing import PublishListingCommand, PublishListingHandler
from src.domain.entities.category import Category
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import InvalidListingTransitionError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
async def draft_listing_id(uow: InMemoryUnitOfWork) -> str:
    category = Category.create(name="PubCat")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    result = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="To Publish Item",
            description="",
            price_amount="15",
            quantity=1,
            location="Oslo",
        )
    )
    return result.listing_id


@pytest.mark.asyncio
async def test_publish_listing(uow: InMemoryUnitOfWork, draft_listing_id: str) -> None:
    result = await PublishListingHandler(uow, NoOpEventPublisher()).handle(
        PublishListingCommand(listing_id=draft_listing_id, seller_id=SELLER)
    )
    assert result.status == "ACTIVE"
    async with uow:
        listing = await uow.listings.get_by_id(ListingId(draft_listing_id))
    assert listing.status.value == "ACTIVE"


@pytest.mark.asyncio
async def test_publish_twice_fails(
    uow: InMemoryUnitOfWork, draft_listing_id: str
) -> None:
    handler = PublishListingHandler(uow, NoOpEventPublisher())
    await handler.handle(
        PublishListingCommand(listing_id=draft_listing_id, seller_id=SELLER)
    )
    with pytest.raises(InvalidListingTransitionError):
        await handler.handle(
            PublishListingCommand(listing_id=draft_listing_id, seller_id=SELLER)
        )
