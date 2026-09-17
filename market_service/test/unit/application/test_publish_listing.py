import pytest
from uuid import uuid4
from src.application.publish_listing import (
    PublishListingCommand,
    PublishListingHandler,
)
from src.domain.events.listing_published import ListingPublished
from src.domain.events.listing_status_changed import ListingStatusChanged
from src.exceptions import InvalidListingTransitionError, SellerMismatchError


class TestPublishListing:
    async def test_publishes_draft_listing_with_both_events(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = PublishListingHandler(uow, event_publisher)

        result = await handler.handle(
            PublishListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
            )
        )

        assert result.status == "ACTIVE"
        assert listing.status.value == "ACTIVE"
        assert uow.committed is True
        assert listing in uow.listings.updated

        assert len(event_publisher.published) == 2
        status_changed, published = event_publisher.published
        assert isinstance(status_changed, ListingStatusChanged)
        assert status_changed.old_status == "DRAFT"
        assert status_changed.new_status == "ACTIVE"
        assert isinstance(published, ListingPublished)
        assert published.listing_id == listing.id.value
        assert published.category_id == listing.category_id.value

    async def test_missing_listing_raises_and_does_not_commit(
        self, uow, event_publisher
    ):
        handler = PublishListingHandler(uow, event_publisher)
        with pytest.raises(Exception):
            await handler.handle(
                PublishListingCommand(
                    listing_id=str(uuid4()),
                    seller_id=str(uuid4()),
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_seller_mismatch_raises(self, uow, event_publisher, make_listing):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = PublishListingHandler(uow, event_publisher)

        with pytest.raises(SellerMismatchError):
            await handler.handle(
                PublishListingCommand(
                    listing_id=listing.id.value,
                    seller_id=str(uuid4()),
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_publishing_non_draft_raises_invalid_transition(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="ACTIVE")
        await uow.listings.add(listing)
        handler = PublishListingHandler(uow, event_publisher)

        with pytest.raises(InvalidListingTransitionError):
            await handler.handle(
                PublishListingCommand(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                )
            )
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_without_event_publisher_still_commits(
        self, uow, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = PublishListingHandler(uow, event_publisher=None)

        result = await handler.handle(
            PublishListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
            )
        )
        assert result.status == "ACTIVE"
        assert uow.committed is True