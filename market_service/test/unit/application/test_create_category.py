"""Unit tests for CreateCategoryHandler — mocked UoW."""

from unittest.mock import AsyncMock

import pytest

from src.application.create_category import (
    CreateCategoryCommand,
    CreateCategoryHandler,
    CreateCategoryResult,
)
from src.domain.events.category_created import CategoryCreated
from src.exceptions import CategoryNotFoundError


async def test_create_category_success(mock_uow, mock_events):
    mock_uow.categories.get_by_name = AsyncMock(return_value=None)
    handler = CreateCategoryHandler(mock_uow, mock_events)

    result = await handler.handle(CreateCategoryCommand(name="Electronics"))

    assert isinstance(result, CreateCategoryResult)
    assert result.name == "Electronics"
    assert result.is_active is True
    mock_uow.categories.add.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    assert isinstance(mock_events.publish.await_args.args[0], CategoryCreated)


async def test_create_category_with_missing_parent(mock_uow, mock_events):
    mock_uow.categories.get_by_name = AsyncMock(return_value=None)
    mock_uow.categories.get_by_id = AsyncMock(
        side_effect=CategoryNotFoundError("missing parent")
    )
    handler = CreateCategoryHandler(mock_uow, mock_events)

    with pytest.raises(CategoryNotFoundError):
        await handler.handle(
            CreateCategoryCommand(
                name="Laptops",
                parent_id="550e8400-e29b-41d4-a716-446655440099",
            )
        )
    mock_uow.categories.add.assert_not_awaited()
