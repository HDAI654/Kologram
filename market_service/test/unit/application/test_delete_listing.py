import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.delete_listing import DeleteListingCommand, DeleteListingHandler
from src.domain.entities.category import Category
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import ListingNotFoundError, SellerMismatchError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"
OTHER = "550e8400-e29b-41d4-a716-446655440099"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
async def listing_id(uow: InMemoryUnitOfWork) -> str:
    category = Category.create(name="DeleteCat")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    result = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="To Be Deleted Item",
            description="",
            price_amount="10",
            quantity=1,
            location="Berlin",
        )
    )
    return result.listing_id


@pytest.mark.asyncio
async def test_delete_listing(uow: InMemoryUnitOfWork, listing_id: str) -> None:
    result = await DeleteListingHandler(uow, NoOpEventPublisher()).handle(
        DeleteListingCommand(listing_id=listing_id, seller_id=SELLER)
    )
    assert result.deleted is True
    with pytest.raises(ListingNotFoundError):
        async with uow:
            await uow.listings.get_by_id(ListingId(listing_id))


@pytest.mark.asyncio
async def test_delete_wrong_seller(uow: InMemoryUnitOfWork, listing_id: str) -> None:
    with pytest.raises(SellerMismatchError):
        await DeleteListingHandler(uow, NoOpEventPublisher()).handle(
            DeleteListingCommand(listing_id=listing_id, seller_id=OTHER)
        )


@pytest.mark.asyncio
async def test_delete_not_found(uow: InMemoryUnitOfWork) -> None:
    with pytest.raises(ListingNotFoundError):
        await DeleteListingHandler(uow, NoOpEventPublisher()).handle(
            DeleteListingCommand(
                listing_id="550e8400-e29b-41d4-a716-446655440099",
                seller_id=SELLER,
            )
        )
