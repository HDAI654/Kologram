import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.application.update_listing import UpdateListingCommand, UpdateListingHandler
from src.domain.entities.category import Category
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import SellerMismatchError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"
OTHER = "550e8400-e29b-41d4-a716-446655440099"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
async def draft_id(uow: InMemoryUnitOfWork) -> str:
    category = Category.create(name="UpdateCat")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()
    result = await CreateListingHandler(uow, NoOpEventPublisher()).handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="Original Title Here",
            description="desc",
            price_amount="100",
            quantity=2,
            location="Vienna",
        )
    )
    return result.listing_id


@pytest.mark.asyncio
async def test_update_listing(uow: InMemoryUnitOfWork, draft_id: str) -> None:
    result = await UpdateListingHandler(uow, NoOpEventPublisher()).handle(
        UpdateListingCommand(
            listing_id=draft_id,
            seller_id=SELLER,
            title="Updated Title Now",
            price_amount="120.50",
        )
    )
    assert result.listing_id == draft_id
    async with uow:
        listing = await uow.listings.get_by_id(ListingId(draft_id))
    assert listing.title.value == "Updated Title Now"
    assert str(listing.price.amount) == "120.50"


@pytest.mark.asyncio
async def test_update_wrong_seller(uow: InMemoryUnitOfWork, draft_id: str) -> None:
    with pytest.raises(SellerMismatchError):
        await UpdateListingHandler(uow, NoOpEventPublisher()).handle(
            UpdateListingCommand(
                listing_id=draft_id,
                seller_id=OTHER,
                title="Hacked Title Now",
            )
        )
