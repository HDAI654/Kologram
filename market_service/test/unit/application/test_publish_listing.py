"""Unit tests for PublishListingHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.publish_listing import (
    PublishListingCommand,
    PublishListingHandler,
    PublishListingResult,
)
from src.exceptions import SellerMismatchError
from market_service.test.unit.application.conftest import LISTING_ID, OTHER_SELLER_ID, SELLER_ID


async def test_publish_listing_success(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = PublishListingHandler(mock_uow, mock_events)

    result = await handler.handle(
        PublishListingCommand(listing_id=LISTING_ID, seller_id=SELLER_ID)
    )

    assert isinstance(result, PublishListingResult)
    assert result.status == "ACTIVE"
    mock_uow.listings.update.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited()


async def test_publish_listing_seller_mismatch(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = PublishListingHandler(mock_uow, mock_events)

    with pytest.raises(SellerMismatchError):
        await handler.handle(
            PublishListingCommand(listing_id=LISTING_ID, seller_id=OTHER_SELLER_ID)
        )
    mock_uow.listings.update.assert_not_awaited()
