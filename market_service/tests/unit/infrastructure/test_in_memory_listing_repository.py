from datetime import datetime, timedelta, timezone

import pytest

from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import ListingNotFoundError
from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryUnitOfWork,
)


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


class TestAdd:
    async def test_stores_listing(self, uow, make_listing):
        listing = make_listing()
        await uow.listings.add(listing)

        assert await uow.listings.get_by_id(listing.id) is listing


class TestGetById:
    async def test_returns_stored_listing(self, uow, make_listing):
        listing = make_listing()
        await uow.listings.add(listing)

        assert await uow.listings.get_by_id(listing.id) is listing

    async def test_raises_when_missing(self, uow):
        with pytest.raises(ListingNotFoundError):
            await uow.listings.get_by_id(ListingId.generate())


class TestUpdate:
    async def test_persists_changes(self, uow, make_listing):
        listing = make_listing()
        await uow.listings.add(listing)

        listing.update_details(title="Updated Title")
        await uow.listings.update(listing)

        stored = await uow.listings.get_by_id(listing.id)
        assert stored.title.value == "Updated Title"

    async def test_missing_raises(self, uow, make_listing):
        with pytest.raises(ListingNotFoundError):
            await uow.listings.update(make_listing())


class TestDelete:
    async def test_removes_listing(self, uow, make_listing):
        listing = make_listing()
        await uow.listings.add(listing)

        await uow.listings.delete(listing.id)

        with pytest.raises(ListingNotFoundError):
            await uow.listings.get_by_id(listing.id)

    async def test_missing_raises(self, uow):
        with pytest.raises(ListingNotFoundError):
            await uow.listings.delete(ListingId.generate())


class TestListBySeller:
    async def test_filters_and_sorts_desc(self, uow, make_listing):
        seller = UserId.generate()
        older = make_listing(seller_id=seller.value)
        newer = make_listing(seller_id=seller.value)
        other = make_listing()

        older.created_at = datetime.now(timezone.utc) - timedelta(days=1)
        newer.created_at = datetime.now(timezone.utc)

        await uow.listings.add(older)
        await uow.listings.add(newer)
        await uow.listings.add(other)

        result = await uow.listings.list_by_seller(seller)

        assert [lst.id for lst in result] == [newer.id, older.id]

    async def test_respects_pagination(self, uow, make_listing):
        seller = UserId.generate()
        for _ in range(5):
            await uow.listings.add(make_listing(seller_id=seller.value))

        page = await uow.listings.list_by_seller(seller, limit=2, offset=1)

        assert len(page) == 2

    async def test_empty_for_unknown_seller(self, uow):
        assert await uow.listings.list_by_seller(UserId.generate()) == []


class TestSearch:
    async def test_matches_title_or_description(self, uow, make_listing):
        match_title = make_listing(title="Vintage Camera")
        match_description = make_listing(
            title="Modern Chair", description="contains camera word"
        )
        non_match = make_listing(title="Lamp", description="Just a lamp")
        for lst in (match_title, match_description, non_match):
            await uow.listings.add(lst)

        result = await uow.listings.search(query="camera")

        assert {lst.id for lst in result} == {
            match_title.id,
            match_description.id,
        }

    async def test_status_filter_case_insensitive(self, uow, make_listing):
        active = make_listing(status="ACTIVE")
        draft = make_listing(status="DRAFT")
        await uow.listings.add(active)
        await uow.listings.add(draft)

        result = await uow.listings.search(status="active")

        assert [lst.id for lst in result] == [active.id]

    async def test_price_range(self, uow, make_listing):
        cheap = make_listing(price_amount="50.00")
        expensive = make_listing(price_amount="500.00")
        await uow.listings.add(cheap)
        await uow.listings.add(expensive)

        result = await uow.listings.search(min_price="10.00", max_price="100.00")

        assert [lst.id for lst in result] == [cheap.id]

    async def test_location_filter_case_insensitive(self, uow, make_listing):
        berlin = make_listing(location="Berlin")
        paris = make_listing(location="Paris")
        await uow.listings.add(berlin)
        await uow.listings.add(paris)

        result = await uow.listings.search(location="berlin")

        assert [lst.id for lst in result] == [berlin.id]

    async def test_seller_filter(self, uow, make_listing):
        seller = UserId.generate()
        mine = make_listing(seller_id=seller.value)
        other = make_listing()
        await uow.listings.add(mine)
        await uow.listings.add(other)

        result = await uow.listings.search(seller_id=seller.value)

        assert [lst.id for lst in result] == [mine.id]

    async def test_category_filter(self, uow, make_listing):
        category_id = "00000000-0000-4000-8000-0000000000aa"
        match = make_listing(category_id=category_id)
        other = make_listing()
        await uow.listings.add(match)
        await uow.listings.add(other)

        result = await uow.listings.search(category_id=category_id)

        assert [lst.id for lst in result] == [match.id]

    async def test_sorts_by_created_at_desc(self, uow, make_listing):
        older = make_listing()
        newer = make_listing()
        older.created_at = datetime.now(timezone.utc) - timedelta(days=1)
        newer.created_at = datetime.now(timezone.utc)
        await uow.listings.add(older)
        await uow.listings.add(newer)

        result = await uow.listings.search()

        assert [lst.id for lst in result] == [newer.id, older.id]

    async def test_empty_store(self, uow):
        assert await uow.listings.search() == []
