"""Unit tests for UpdateListingHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.update_listing import (
    UpdateListingCommand,
    UpdateListingHandler,
    UpdateListingResult,
)
from src.exceptions import SellerMismatchError
from market_service.test.unit.application.conftest import LISTING_ID, OTHER_SELLER_ID, SELLER_ID


async def test_update_listing_success(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = UpdateListingHandler(mock_uow, mock_events)

    result = await handler.handle(
        UpdateListingCommand(
            listing_id=LISTING_ID,
            seller_id=SELLER_ID,
            title="Updated Title",
            price_amount="1500.00",
        )
    )

    assert isinstance(result, UpdateListingResult)
    assert result.listing_id == LISTING_ID
    mock_uow.listings.update.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


async def test_update_listing_seller_mismatch(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = UpdateListingHandler(mock_uow, mock_events)

    with pytest.raises(SellerMismatchError):
        await handler.handle(
            UpdateListingCommand(
                listing_id=LISTING_ID,
                seller_id=OTHER_SELLER_ID,
                title="Hijack",
            )
        )
    mock_uow.listings.update.assert_not_awaited()
