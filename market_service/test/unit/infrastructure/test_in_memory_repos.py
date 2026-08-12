import pytest

from src.domain.entities.category import Category
from src.domain.entities.listing import Listing
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import CategoryNotFoundError, ListingNotFoundError
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork

SELLER = "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.asyncio
async def test_category_crud() -> None:
    uow = InMemoryUnitOfWork()
    cat = Category.create(name="Fashion")
    async with uow:
        await uow.categories.add(cat)
        await uow.commit()
        loaded = await uow.categories.get_by_id(cat.id)
        assert loaded.name.value == "Fashion"
        by_name = await uow.categories.get_by_name(CategoryName("Fashion"))
        assert by_name is not None
        all_cats = await uow.categories.list_all()
        assert len(all_cats) == 1


@pytest.mark.asyncio
async def test_listing_crud_and_search() -> None:
    uow = InMemoryUnitOfWork()
    cat = Category.create(name="Tools")
    listing = Listing.create(
        seller_id=SELLER,
        category_id=cat.id.value,
        title="Hammer",
        description="Steel head",
        price_amount="12.50",
        quantity=3,
        location="Madrid",
    )
    async with uow:
        await uow.categories.add(cat)
        await uow.listings.add(listing)
        await uow.commit()

        loaded = await uow.listings.get_by_id(listing.id)
        assert loaded.title.value == "Hammer"

        by_seller = await uow.listings.list_by_seller(UserId(SELLER))
        assert len(by_seller) == 1

        found = await uow.listings.search(query="Hammer", status="DRAFT")
        assert len(found) == 1

        listing.publish()
        await uow.listings.update(listing)
        await uow.commit()
        active = await uow.listings.search(status="ACTIVE")
        assert len(active) == 1


@pytest.mark.asyncio
async def test_not_found() -> None:
    uow = InMemoryUnitOfWork()
    with pytest.raises(ListingNotFoundError):
        async with uow:
            await uow.listings.get_by_id(
                ListingId("550e8400-e29b-41d4-a716-446655440099")
            )
    with pytest.raises(CategoryNotFoundError):
        async with uow:
            await uow.categories.get_by_id(
                CategoryId("550e8400-e29b-41d4-a716-446655440099")
            )
