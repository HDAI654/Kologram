import pytest
from uuid import uuid4
from src.application.update_listing import (
    UpdateListingCommand,
    UpdateListingHandler,
)
from src.domain.events.listing_updated import ListingUpdated
from src.exceptions import ListingNotEditableError, SellerMismatchError


class TestUpdateListing:
    async def test_updates_editable_listing_and_publishes_event(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = UpdateListingHandler(uow, event_publisher)

        result = await handler.handle(
            UpdateListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                title="Updated Title",
                price_amount="250.00",
                quantity=10,
                location="Berlin",
            )
        )

        assert result.status == "DRAFT"
        assert listing.title.value == "Updated Title"
        assert str(listing.price.amount) == "250.00"
        assert listing.quantity.value == 10
        assert listing.location.value == "Berlin"
        assert uow.committed is True
        assert listing in uow.listings.updated

        assert len(event_publisher.published) == 1
        event = event_publisher.published[0]
        assert isinstance(event, ListingUpdated)
        assert event.listing_id == listing.id.value
        assert event.seller_id == listing.seller_id.value

    async def test_partial_update_only_changes_provided_fields(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(
            status="DRAFT", title="Original Title", location="New York"
        )
        await uow.listings.add(listing)
        handler = UpdateListingHandler(uow, event_publisher)

        await handler.handle(
            UpdateListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                title="New Title",
            )
        )

        assert listing.title.value == "New Title"
        assert listing.location.value == "New York"

    async def test_missing_listing_raises(self, uow, event_publisher):
        handler = UpdateListingHandler(uow, event_publisher)
        with pytest.raises(Exception):
            await handler.handle(
                UpdateListingCommand(
                    listing_id=str(uuid4()),
                    seller_id=str(uuid4()),
                    title="Updated",
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_seller_mismatch_raises(self, uow, event_publisher, make_listing):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = UpdateListingHandler(uow, event_publisher)

        with pytest.raises(SellerMismatchError):
            await handler.handle(
                UpdateListingCommand(
                    listing_id=listing.id.value,
                    seller_id=str(uuid4()),
                    title="Hacked",
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_non_editable_listing_raises_domain_error(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="SOLD")
        await uow.listings.add(listing)
        handler = UpdateListingHandler(uow, event_publisher)

        with pytest.raises(ListingNotEditableError):
            await handler.handle(
                UpdateListingCommand(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                    title="Should Not Apply",
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_without_event_publisher_still_commits(
        self, uow, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = UpdateListingHandler(uow, event_publisher=None)

        result = await handler.handle(
            UpdateListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                title="Updated Title",
            )
        )
        assert result.status == "DRAFT"
        assert uow.committed is True