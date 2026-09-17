import pytest
from uuid import uuid4
from src.application.get_listing import GetListingHandler, GetListingQuery


class TestGetListing:
    async def test_returns_complete_snapshot(self, uow, make_listing):
        listing = make_listing(
            title="Vintage Camera",
            description="Great condition",
            price_amount="250.50",
            currency="EUR",
            quantity=2,
            location="Berlin",
        )
        await uow.listings.add(listing)

        result = await GetListingHandler(uow).handle(
            GetListingQuery(listing_id=listing.id.value)
        )

        assert result.listing_id == listing.id.value
        assert result.seller_id == listing.seller_id.value
        assert result.category_id == listing.category_id.value
        assert result.title == "Vintage Camera"
        assert result.description == "Great condition"
        assert result.price_amount == "250.50"
        assert result.currency == "EUR"
        assert result.quantity == 2
        assert result.status == "DRAFT"
        assert result.location == "Berlin"
        assert result.images == []
        assert result.created_at == listing.created_at.isoformat()
        assert result.updated_at == listing.updated_at.isoformat()

    async def test_images_are_sorted_by_sort_order(self, uow, make_listing):
        listing = make_listing()
        listing.add_image(url="https://example.com/second.jpg", sort_order=5)
        listing.add_image(url="https://example.com/first.jpg", sort_order=1)
        await uow.listings.add(listing)

        result = await GetListingHandler(uow).handle(
            GetListingQuery(listing_id=listing.id.value)
        )

        assert [img.sort_order for img in result.images] == [1, 5]
        assert [img.url for img in result.images] == [
            "https://example.com/first.jpg",
            "https://example.com/second.jpg",
        ]

    async def test_missing_listing_propagates(self, uow):
        handler = GetListingHandler(uow)
        with pytest.raises(Exception):
            await handler.handle(GetListingQuery(listing_id=str(uuid4())))
