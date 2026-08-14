"""Unit tests for ListSellerListingsHandler — mocked UoW."""

from unittest.mock import AsyncMock

from src.application.list_seller_listings import (
    ListSellerListingsHandler,
    ListSellerListingsQuery,
    ListSellerListingsResult,
)
from market_service.test.unit.application.conftest import SELLER_ID


async def test_list_seller_listings(mock_uow, sample_listing):
    mock_uow.listings.list_by_seller = AsyncMock(return_value=[sample_listing])
    handler = ListSellerListingsHandler(mock_uow)

    result = await handler.handle(
        ListSellerListingsQuery(seller_id=SELLER_ID, limit=10, offset=0)
    )

    assert isinstance(result, ListSellerListingsResult)
    assert len(result.items) == 1
    assert result.items[0].seller_id == SELLER_ID
    mock_uow.listings.list_by_seller.assert_awaited_once()
