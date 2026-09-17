import pytest
from uuid import uuid4
from src.application.create_listing import (
    CreateListingCommand,
    CreateListingHandler,
)
from src.domain.events.listing_created import ListingCreated
from src.exceptions import CategoryInactiveError, CategoryNotFoundError


def _command(**overrides) -> CreateListingCommand:
    base = dict(
        seller_id=str(uuid4()),
        category_id=str(uuid4()),
        title="Test Listing",
        description="A description",
        price_amount="100.00",
        quantity=3,
        location="New York",
        currency="USD",
    )
    base.update(overrides)
    return CreateListingCommand(**base)


class TestCreateListing:
    async def test_creates_listing_in_draft(self, uow, event_publisher, make_category):
        category = make_category()
        # Use the category's generated id so the FK lookup succeeds.
        await uow.categories.add(category)
        handler = CreateListingHandler(uow, event_publisher)

        result = await handler.handle(_command(category_id=category.id.value))

        assert result.status == "DRAFT"
        assert result.listing_id
        assert uow.committed is True
        assert len(uow.listings.added) == 1

        assert len(event_publisher.published) == 1
        event = event_publisher.published[0]
        assert isinstance(event, ListingCreated)
        assert event.listing_id == result.listing_id
        assert event.category_id == category.id.value
        assert event.status == "DRAFT"

    async def test_creates_listing_with_images_in_order(
        self, uow, event_publisher, make_category
    ):
        category = make_category()
        await uow.categories.add(category)
        handler = CreateListingHandler(uow, event_publisher)

        await handler.handle(
            _command(
                category_id=category.id.value,
                image_urls=(
                    "https://example.com/a.jpg",
                    "https://example.com/b.jpg",
                ),
            )
        )

        listing = uow.listings.added[0]
        assert [img.url.value for img in listing.images] == [
            "https://example.com/a.jpg",
            "https://example.com/b.jpg",
        ]
        assert [img.sort_order.value for img in listing.images] == [0, 1]

    async def test_missing_category_raises_and_does_not_commit(
        self, uow, event_publisher
    ):
        handler = CreateListingHandler(uow, event_publisher)
        with pytest.raises(CategoryNotFoundError):
            await handler.handle(_command())
        assert uow.committed is False
        assert event_publisher.published == []

    async def test_inactive_category_raises_and_does_not_commit(
        self, uow, event_publisher, make_category
    ):
        category = make_category(is_active=False)
        await uow.categories.add(category)
        handler = CreateListingHandler(uow, event_publisher)

        with pytest.raises(CategoryInactiveError):
            await handler.handle(_command(category_id=category.id.value))

        assert uow.committed is False
        assert uow.listings.added == []
        assert event_publisher.published == []

    async def test_without_event_publisher_still_commits(self, uow, make_category):
        category = make_category()
        await uow.categories.add(category)
        handler = CreateListingHandler(uow, event_publisher=None)
        result = await handler.handle(_command(category_id=category.id.value))
        assert result.status == "DRAFT"
        assert uow.committed is True
