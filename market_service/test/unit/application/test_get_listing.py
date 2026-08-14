"""Unit tests for GetListingHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.get_listing import (
    GetListingHandler,
    GetListingQuery,
    GetListingResult,
)
from src.exceptions import ListingNotFoundError
from market_service.test.unit.application.conftest import LISTING_ID


async def test_get_listing_success(mock_uow, sample_listing):
    mock_uow.listings.get_by_id = AsyncMock(return_value=sample_listing)
    handler = GetListingHandler(mock_uow)

    result = await handler.handle(GetListingQuery(listing_id=LISTING_ID))

    assert isinstance(result, GetListingResult)
    assert result.listing_id == LISTING_ID
    assert result.title == sample_listing.title.value
    mock_uow.listings.get_by_id.assert_awaited_once()


async def test_get_listing_not_found(mock_uow):
    mock_uow.listings.get_by_id = AsyncMock(side_effect=ListingNotFoundError("missing"))
    handler = GetListingHandler(mock_uow)

    with pytest.raises(ListingNotFoundError):
        await handler.handle(GetListingQuery(listing_id=LISTING_ID))
