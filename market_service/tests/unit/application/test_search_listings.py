from src.application.search_listings import (
    SearchListingsHandler,
    SearchListingsQuery,
)
from uuid import uuid4


class TestSearchListings:
    async def test_default_filter_returns_only_active(self, uow, make_listing):
        active = make_listing(status="ACTIVE")
        draft = make_listing(status="DRAFT")
        await uow.listings.add(active)
        await uow.listings.add(draft)

        result = await SearchListingsHandler(uow).handle(SearchListingsQuery())

        ids = {item.listing_id for item in result.items}
        assert ids == {active.id.value}

    async def test_query_filter_matches_title(self, uow, make_listing):
        wanted = make_listing(status="ACTIVE", title="Vintage Camera")
        other = make_listing(status="ACTIVE", title="Modern Chair")
        await uow.listings.add(wanted)
        await uow.listings.add(other)

        result = await SearchListingsHandler(uow).handle(
            SearchListingsQuery(query="camera")
        )
        assert [item.listing_id for item in result.items] == [wanted.id.value]

    async def test_limit_is_clamped_to_range(self, uow, make_listing):
        for _ in range(3):
            await uow.listings.add(make_listing(status="ACTIVE"))

        # limit=0 clamps to 1, limit=1000 clamps to 100.
        low = await SearchListingsHandler(uow).handle(SearchListingsQuery(limit=0))
        assert low.limit == 1

        high = await SearchListingsHandler(uow).handle(SearchListingsQuery(limit=1000))
        assert high.limit == 100

    async def test_negative_offset_clamped(self, uow, make_listing):
        await uow.listings.add(make_listing(status="ACTIVE"))
        result = await SearchListingsHandler(uow).handle(SearchListingsQuery(offset=-5))
        assert result.offset == 0

    async def test_category_and_price_filters(self, uow, make_listing):
        category_a = str(uuid4())
        category_b = str(uuid4())
        cheap = make_listing(
            status="ACTIVE", category_id=category_a, price_amount="50.00"
        )
        expensive = make_listing(
            status="ACTIVE", category_id=category_a, price_amount="500.00"
        )
        other = make_listing(
            status="ACTIVE", category_id=category_b, price_amount="50.00"
        )
        for lst in (cheap, expensive, other):
            await uow.listings.add(lst)

        result = await SearchListingsHandler(uow).handle(
            SearchListingsQuery(
                category_id=category_a, min_price="10.00", max_price="100.00"
            )
        )
        assert [item.listing_id for item in result.items] == [cheap.id.value]

    async def test_seller_and_location_filters(self, uow, make_listing):
        seller = str(uuid4())
        match = make_listing(status="ACTIVE", seller_id=seller, location="Berlin")
        non_match_seller = make_listing(
            status="ACTIVE",
            seller_id=str(uuid4()),
            location="Berlin",
        )
        non_match_location = make_listing(
            status="ACTIVE", seller_id=seller, location="Paris"
        )
        for lst in (match, non_match_seller, non_match_location):
            await uow.listings.add(lst)

        result = await SearchListingsHandler(uow).handle(
            SearchListingsQuery(seller_id=seller, location="berlin")
        )
        assert [item.listing_id for item in result.items] == [match.id.value]

    async def test_pagination(self, uow, make_listing):
        for _ in range(5):
            await uow.listings.add(make_listing(status="ACTIVE"))

        result = await SearchListingsHandler(uow).handle(
            SearchListingsQuery(limit=2, offset=1)
        )
        assert len(result.items) == 2
        assert result.limit == 2
        assert result.offset == 1

    async def test_empty_result(self, uow):
        result = await SearchListingsHandler(uow).handle(SearchListingsQuery())
        assert result.items == []
        assert result.limit == 20
        assert result.offset == 0
