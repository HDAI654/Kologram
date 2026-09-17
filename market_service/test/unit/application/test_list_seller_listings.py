from uuid import uuid4
from src.application.list_seller_listings import (
    ListSellerListingsHandler,
    ListSellerListingsQuery,
)


class TestListSellerListings:
    async def test_returns_only_seller_listings(self, uow, make_listing):
        seller_id = str(uuid4())
        other_seller = str(uuid4())
        await uow.listings.add(make_listing(seller_id=seller_id))
        await uow.listings.add(make_listing(seller_id=seller_id))
        await uow.listings.add(make_listing(seller_id=other_seller))

        result = await ListSellerListingsHandler(uow).handle(
            ListSellerListingsQuery(seller_id=seller_id)
        )

        assert len(result.items) == 2
        assert all(item.seller_id == seller_id for item in result.items)

    async def test_applies_limit_and_offset(self, uow, make_listing):
        seller_id = str(uuid4())
        for _ in range(5):
            await uow.listings.add(make_listing(seller_id=seller_id))

        result = await ListSellerListingsHandler(uow).handle(
            ListSellerListingsQuery(seller_id=seller_id, limit=2, offset=1)
        )

        assert len(result.items) == 2

    async def test_non_positive_limit_defaults_to_50(self, uow, make_listing):
        seller_id = str(uuid4())
        for _ in range(3):
            await uow.listings.add(make_listing(seller_id=seller_id))

        result = await ListSellerListingsHandler(uow).handle(
            ListSellerListingsQuery(seller_id=seller_id, limit=0)
        )
        assert len(result.items) == 3

    async def test_negative_offset_is_clamped_to_zero(
        self, uow, make_listing
    ):
        seller_id = str(uuid4())
        await uow.listings.add(make_listing(seller_id=seller_id))

        result = await ListSellerListingsHandler(uow).handle(
            ListSellerListingsQuery(seller_id=seller_id, offset=-10)
        )
        assert len(result.items) == 1

    async def test_empty_for_unknown_seller(self, uow):
        result = await ListSellerListingsHandler(uow).handle(
            ListSellerListingsQuery(
                seller_id=str(uuid4())
            )
        )
        assert result.items == ()