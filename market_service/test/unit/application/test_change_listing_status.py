import pytest
from uuid import uuid4
from src.application.change_listing_status import (
    ChangeListingStatusCommand,
    ChangeListingStatusHandler,
)
from src.domain.events.listing_status_changed import ListingStatusChanged
from src.exceptions import (
    InvalidListingTransitionError,
    SellerMismatchError,
)


class TestChangeListingStatus:
    async def test_cancel_draft_listing_publishes_event_and_commits(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = ChangeListingStatusHandler(uow, event_publisher)

        result = await handler.handle(
            ChangeListingStatusCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                new_status="CANCELLED",
            )
        )

        assert result.listing_id == listing.id.value
        assert result.status == "CANCELLED"
        assert uow.committed is True
        assert uow.commit_count == 1
        assert uow.rolled_back is False
        assert listing in uow.listings.updated

        assert len(event_publisher.published) == 1
        event = event_publisher.published[0]
        assert isinstance(event, ListingStatusChanged)
        assert event.listing_id == listing.id.value
        assert event.seller_id == listing.seller_id.value
        assert event.old_status == "DRAFT"
        assert event.new_status == "CANCELLED"

    async def test_mark_active_listing_as_sold(self, uow, event_publisher, make_listing):
        listing = make_listing(status="ACTIVE")
        await uow.listings.add(listing)
        handler = ChangeListingStatusHandler(uow, event_publisher)

        result = await handler.handle(
            ChangeListingStatusCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                new_status="SOLD",
            )
        )

        assert result.status == "SOLD"
        assert event_publisher.published[0].old_status == "ACTIVE"
        assert event_publisher.published[0].new_status == "SOLD"

    async def test_missing_listing_propagates_and_does_not_commit(
        self, uow, event_publisher
    ):
        handler = ChangeListingStatusHandler(uow, event_publisher)
        with pytest.raises(Exception):
            await handler.handle(
                ChangeListingStatusCommand(
                    listing_id=str(uuid4()),
                    seller_id=str(uuid4()),
                    new_status="CANCELLED",
                )
            )
        assert uow.committed is False
        assert uow.rolled_back is True
        assert event_publisher.published == []

    async def test_seller_mismatch_raises_and_does_not_commit(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = ChangeListingStatusHandler(uow, event_publisher)

        with pytest.raises(SellerMismatchError):
            await handler.handle(
                ChangeListingStatusCommand(
                    listing_id=listing.id.value,
                    seller_id=str(uuid4()),
                    new_status="CANCELLED",
                )
            )

        assert listing.status.value == "DRAFT"
        assert uow.committed is False
        assert uow.rolled_back is True
        assert event_publisher.published == []

    async def test_invalid_transition_raises_and_does_not_commit(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = ChangeListingStatusHandler(uow, event_publisher)

        with pytest.raises(InvalidListingTransitionError):
            await handler.handle(
                ChangeListingStatusCommand(
                    listing_id=listing.id.value,
                    seller_id=listing.seller_id.value,
                    new_status="SOLD",
                )
            )

        assert listing.status.value == "DRAFT"
        assert uow.committed is False
        assert uow.rolled_back is True
        assert event_publisher.published == []

    async def test_without_event_publisher_still_commits(
        self, uow, make_listing
    ):
        listing = make_listing(status="DRAFT")
        await uow.listings.add(listing)
        handler = ChangeListingStatusHandler(uow, event_publisher=None)

        result = await handler.handle(
            ChangeListingStatusCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
                new_status="CANCELLED",
            )
        )
        assert result.status == "CANCELLED"
        assert uow.committed is True