import pytest

from src.application.create_listing import CreateListingCommand, CreateListingHandler
from src.domain.entities.category import Category
from src.domain.value_objects.listing_id import ListingId
from src.exceptions import CategoryInactiveError, CategoryNotFoundError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.mark.asyncio
async def test_create_listing_success(uow: InMemoryUnitOfWork) -> None:
    category = Category.create(name="Electronics")
    async with uow:
        await uow.categories.add(category)
        await uow.commit()

    handler = CreateListingHandler(uow, NoOpEventPublisher())
    result = await handler.handle(
        CreateListingCommand(
            seller_id=SELLER,
            category_id=category.id.value,
            title="MacBook Pro 14",
            description="M3, 16GB",
            price_amount="1999.00",
            quantity=1,
            location="Berlin",
            image_urls=("https://cdn.example.com/mbp.jpg",),
        )
    )
    assert result.status == "DRAFT"
    assert result.listing_id

    async with uow:
        listing = await uow.listings.get_by_id(ListingId(result.listing_id))
    assert listing.title.value == "MacBook Pro 14"
    assert len(listing.images) == 1


@pytest.mark.asyncio
async def test_create_listing_unknown_category(uow: InMemoryUnitOfWork) -> None:
    handler = CreateListingHandler(uow, NoOpEventPublisher())
    with pytest.raises(CategoryNotFoundError):
        await handler.handle(
            CreateListingCommand(
                seller_id=SELLER,
                category_id="550e8400-e29b-41d4-a716-446655440099",
                title="Item",
                description="",
                price_amount="10",
                quantity=1,
                location="Paris",
            )
        )


@pytest.mark.asyncio
async def test_create_listing_inactive_category(uow: InMemoryUnitOfWork) -> None:
    category = Category.create(name="Deprecated", is_active=False)
    async with uow:
        await uow.categories.add(category)
        await uow.commit()

    handler = CreateListingHandler(uow, NoOpEventPublisher())
    with pytest.raises(CategoryInactiveError):
        await handler.handle(
            CreateListingCommand(
                seller_id=SELLER,
                category_id=category.id.value,
                title="Item",
                description="",
                price_amount="10",
                quantity=1,
                location="Paris",
            )
        )
