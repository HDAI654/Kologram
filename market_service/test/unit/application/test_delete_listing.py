import pytest
from uuid import uuid4
from src.application.delete_listing import (
    DeleteListingCommand,
    DeleteListingHandler,
)
from src.domain.events.listing_deleted import ListingDeleted
from src.exceptions import SellerMismatchError


class TestDeleteListing:
    async def test_deletes_owned_listing(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing()
        await uow.listings.add(listing)
        handler = DeleteListingHandler(uow, event_publisher)

        result = await handler.handle(
            DeleteListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
            )
        )

        assert result.deleted is True
        assert result.listing_id == listing.id.value
        assert uow.listings.deleted == [listing.id.value]
        assert uow.committed is True

        assert len(event_publisher.published) == 1
        event = event_publisher.published[0]
        assert isinstance(event, ListingDeleted)
        assert event.listing_id == listing.id.value
        assert event.seller_id == listing.seller_id.value

    async def test_missing_listing_raises_and_does_not_commit(
        self, uow, event_publisher
    ):
        handler = DeleteListingHandler(uow, event_publisher)
        with pytest.raises(Exception):
            await handler.handle(
                DeleteListingCommand(
                    listing_id=str(uuid4()),
                    seller_id=str(uuid4()),
                )
            )
        assert uow.committed is False
        assert uow.rolled_back is True
        assert uow.listings.deleted == []
        assert event_publisher.published == []

    async def test_seller_mismatch_raises_and_does_not_delete(
        self, uow, event_publisher, make_listing
    ):
        listing = make_listing()
        await uow.listings.add(listing)
        handler = DeleteListingHandler(uow, event_publisher)

        with pytest.raises(SellerMismatchError):
            await handler.handle(
                DeleteListingCommand(
                    listing_id=listing.id.value,
                    seller_id=str(uuid4()),
                )
            )

        assert uow.listings.deleted == []
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_without_event_publisher_still_commits(
        self, uow, make_listing
    ):
        listing = make_listing()
        await uow.listings.add(listing)
        handler = DeleteListingHandler(uow, event_publisher=None)
        result = await handler.handle(
            DeleteListingCommand(
                listing_id=listing.id.value,
                seller_id=listing.seller_id.value,
            )
        )
        assert result.deleted is True
        assert uow.committed is True