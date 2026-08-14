"""Unit tests for ListCategoriesHandler — mocked UoW."""

from unittest.mock import AsyncMock

from src.application.list_categories import (
    ListCategoriesHandler,
    ListCategoriesQuery,
    ListCategoriesResult,
)


async def test_list_categories(mock_uow, active_category):
    mock_uow.categories.list_all = AsyncMock(return_value=[active_category])
    handler = ListCategoriesHandler(mock_uow)

    result = await handler.handle(ListCategoriesQuery(active_only=True))

    assert isinstance(result, ListCategoriesResult)
    assert len(result.items) == 1
    assert result.items[0].name == active_category.name.value
    mock_uow.categories.list_all.assert_awaited_once_with(active_only=True)
