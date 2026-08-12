"""InMemoryListingRepository — every method and exception path."""

from __future__ import annotations

import pytest

from src.domain.entities.category import Category
from src.domain.entities.listing import Listing
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import ListingNotFoundError
from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryListingRepository,
    InMemoryUnitOfWork,
)

SELLER = "550e8400-e29b-41d4-a716-446655440000"
OTHER = "550e8400-e29b-41d4-a716-446655440099"
MISSING = "550e8400-e29b-41d4-a716-446655440050"


def _listing(
    title: str = "Item Alpha", seller: str = SELLER, status: str = "DRAFT"
) -> Listing:
    category = Category.create(name="CatForListing")
    return Listing.create(
        seller_id=seller,
        category_id=category.id.value,
        title=title,
        description="desc",
        price_amount="25.00",
        quantity=1,
        location="Berlin",
        status=status,
    )


@pytest.fixture
def repo() -> InMemoryListingRepository:
    return InMemoryListingRepository({})


@pytest.mark.asyncio
async def test_add_get_update_delete(repo: InMemoryListingRepository) -> None:
    listing = _listing()
    await repo.add(listing)
    got = await repo.get_by_id(listing.id)
    assert got.title.value == "Item Alpha"

    listing.update_details(title="Item Beta Updated")
    await repo.update(listing)
    got = await repo.get_by_id(listing.id)
    assert got.title.value == "Item Beta Updated"

    await repo.delete(listing.id)
    with pytest.raises(ListingNotFoundError):
        await repo.get_by_id(listing.id)


@pytest.mark.asyncio
async def test_get_not_found(repo: InMemoryListingRepository) -> None:
    with pytest.raises(ListingNotFoundError):
        await repo.get_by_id(ListingId(MISSING))


@pytest.mark.asyncio
async def test_update_not_found(repo: InMemoryListingRepository) -> None:
    listing = _listing()
    with pytest.raises(ListingNotFoundError):
        await repo.update(listing)


@pytest.mark.asyncio
async def test_delete_not_found(repo: InMemoryListingRepository) -> None:
    with pytest.raises(ListingNotFoundError):
        await repo.delete(ListingId(MISSING))


@pytest.mark.asyncio
async def test_list_by_seller(repo: InMemoryListingRepository) -> None:
    a = _listing("Seller A Item One")
    b = _listing("Seller A Item Two")
    c = _listing("Other Seller Item", seller=OTHER)
    await repo.add(a)
    await repo.add(b)
    await repo.add(c)
    items = await repo.list_by_seller(UserId(SELLER), limit=10, offset=0)
    assert len(items) == 2
    assert all(i.seller_id.value == SELLER for i in items)
    page = await repo.list_by_seller(UserId(SELLER), limit=1, offset=1)
    assert len(page) == 1


@pytest.mark.asyncio
async def test_search_filters(repo: InMemoryListingRepository) -> None:
    listing = _listing("Searchable Camera Gear")
    await repo.add(listing)
    by_query = await repo.search(query="Camera", limit=20, offset=0)
    assert len(by_query) == 1
    by_status = await repo.search(status="DRAFT", limit=20, offset=0)
    assert len(by_status) >= 1
    by_seller = await repo.search(seller_id=SELLER, limit=20, offset=0)
    assert len(by_seller) >= 1
    by_location = await repo.search(location="Berlin", limit=20, offset=0)
    assert len(by_location) >= 1
    empty = await repo.search(query="zzzz-no-match", limit=20, offset=0)
    assert empty == []
