import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.publish_listing import PublishListingCommand, PublishListingHandler
from src.application.search_listings import SearchListingsHandler, SearchListingsQuery
from src.domain.entities.category import Category
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.mark.asyncio
async def test_search_listings(uow: InMemoryUnitOfWork) -> None:
    category = Category.create(name="SearchCat")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    created = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="Searchable Camera",
            description="DSLR",
            price_amount="400",
            quantity=1,
            location="Rome",
        )
    )
    await PublishListingHandler(uow, NoOpEventPublisher()).handle(
        PublishListingCommand(listing_id=created.listing_id, seller_id=SELLER)
    )
    result = await SearchListingsHandler(uow).handle(
        SearchListingsQuery(query="Camera", status="ACTIVE")
    )
    assert any(i.listing_id == created.listing_id for i in result.items)
