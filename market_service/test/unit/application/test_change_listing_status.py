"""Unit tests for ChangeListingStatusHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.change_listing_status import (
    ChangeListingStatusCommand,
    ChangeListingStatusHandler,
    ChangeListingStatusResult,
)
from src.exceptions import SellerMismatchError
from market_service.test.unit.application.conftest import (
    LISTING_ID,
    OTHER_SELLER_ID,
    SELLER_ID,
)


async def test_change_status_success(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = ChangeListingStatusHandler(mock_uow, mock_events)

    result = await handler.handle(
        ChangeListingStatusCommand(
            listing_id=LISTING_ID,
            seller_id=SELLER_ID,
            new_status="CANCELLED",
        )
    )

    assert isinstance(result, ChangeListingStatusResult)
    assert result.status == "CANCELLED"
    mock_uow.listings.update.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


async def test_change_status_seller_mismatch(mock_uow, mock_events, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = ChangeListingStatusHandler(mock_uow, mock_events)

    with pytest.raises(SellerMismatchError):
        await handler.handle(
            ChangeListingStatusCommand(
                listing_id=LISTING_ID,
                seller_id=OTHER_SELLER_ID,
                new_status="CANCELLED",
            )
        )
    mock_uow.listings.update.assert_not_awaited()
