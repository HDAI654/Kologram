"""Unit tests for SearchListingsHandler — mocked UoW."""

from unittest.mock import AsyncMock

from src.application.search_listings import (
    SearchListingsHandler,
    SearchListingsQuery,
    SearchListingsResult,
)


async def test_search_listings(mock_uow, sample_listing):
    mock_uow.listings.search = AsyncMock(return_value=[sample_listing])
    handler = SearchListingsHandler(mock_uow)

    result = await handler.handle(
        SearchListingsQuery(query="MacBook", limit=10, offset=0)
    )

    assert isinstance(result, SearchListingsResult)
    assert len(result.items) == 1
    assert result.items[0].listing_id == sample_listing.id.value
    mock_uow.listings.search.assert_awaited_once()
