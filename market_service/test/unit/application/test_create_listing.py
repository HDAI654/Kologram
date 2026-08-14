"""Unit tests for CreateListingHandler — pure application, mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.create_listing import (
    CreateListingCommand,
    CreateListingHandler,
    CreateListingResult,
)
from src.domain.events.listing_created import ListingCreated
from src.exceptions import CategoryInactiveError, CategoryNotFoundError
from market_service.test.unit.application.conftest import CATEGORY_ID, SELLER_ID


async def test_create_listing_success(mock_uow, mock_events, active_category):
    mock_uow.categories.get_by_id = AsyncMock(return_value=active_category)
    handler = CreateListingHandler(mock_uow, mock_events)

    result = await handler.handle(
        CreateListingCommand(
            seller_id=SELLER_ID,
            category_id=CATEGORY_ID,
            title="MacBook Pro 14",
            description="M3, 16GB",
            price_amount="1999.00",
            quantity=1,
            location="Berlin",
            image_urls=("https://cdn.example.com/mbp.jpg",),
        )
    )

    assert isinstance(result, CreateListingResult)
    assert result.status == "DRAFT"
    assert result.listing_id
    mock_uow.listings.add.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    assert isinstance(mock_events.publish.await_args.args[0], ListingCreated)


async def test_create_listing_unknown_category(mock_uow, mock_events):
    mock_uow.categories.get_by_id = AsyncMock(
        side_effect=CategoryNotFoundError("missing")
    )
    handler = CreateListingHandler(mock_uow, mock_events)

    with pytest.raises(CategoryNotFoundError):
        await handler.handle(
            CreateListingCommand(
                seller_id=SELLER_ID,
                category_id="550e8400-e29b-41d4-a716-446655440099",
                title="Item",
                description="",
                price_amount="10",
                quantity=1,
                location="Paris",
            )
        )
    mock_uow.listings.add.assert_not_awaited()


async def test_create_listing_inactive_category(
    mock_uow, mock_events, inactive_category
):
    mock_uow.categories.get_by_id = AsyncMock(return_value=inactive_category)
    handler = CreateListingHandler(mock_uow, mock_events)

    with pytest.raises(CategoryInactiveError):
        await handler.handle(
            CreateListingCommand(
                seller_id=SELLER_ID,
                category_id=inactive_category.id.value,
                title="Item",
                description="",
                price_amount="10",
                quantity=1,
                location="Paris",
            )
        )
    mock_uow.listings.add.assert_not_awaited()
