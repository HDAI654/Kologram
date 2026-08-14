"""Unit tests for DeleteListingHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.delete_listing import (
    DeleteListingCommand,
    DeleteListingHandler,
    DeleteListingResult,
)
from src.exceptions import SellerMismatchError
from market_service.test.unit.application.conftest import LISTING_ID, OTHER_SELLER_ID, SELLER_ID


async def test_delete_listing_success(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = DeleteListingHandler(mock_uow, mock_events)

    result = await handler.handle(
        DeleteListingCommand(listing_id=LISTING_ID, seller_id=SELLER_ID)
    )

    assert isinstance(result, DeleteListingResult)
    assert result.deleted is True
    mock_uow.listings.delete.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


async def test_delete_listing_seller_mismatch(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = DeleteListingHandler(mock_uow, mock_events)

    with pytest.raises(SellerMismatchError):
        await handler.handle(
            DeleteListingCommand(listing_id=LISTING_ID, seller_id=OTHER_SELLER_ID)
        )
    mock_uow.listings.delete.assert_not_awaited()
