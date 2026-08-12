"""InMemoryCategoryRepository — every method and exception path."""

from __future__ import annotations

import pytest

from src.domain.entities.category import Category
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import CategoryNotFoundError
from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryCategoryRepository,
)


@pytest.fixture
def repo() -> InMemoryCategoryRepository:
    return InMemoryCategoryRepository({})


@pytest.mark.asyncio
async def test_add_get_update(repo: InMemoryCategoryRepository) -> None:
    cat = Category.create(name="Electronics")
    await repo.add(cat)
    got = await repo.get_by_id(cat.id)
    assert got.name.value == "Electronics"
    by_name = await repo.get_by_name(CategoryName("Electronics"))
    assert by_name is not None
    assert await repo.get_by_name(CategoryName("Missing Name")) is None

    cat.deactivate() if hasattr(cat, "deactivate") else setattr(cat, "is_active", False)
    await repo.update(cat)
    again = await repo.get_by_id(cat.id)
    assert again.is_active is False


@pytest.mark.asyncio
async def test_get_not_found(repo: InMemoryCategoryRepository) -> None:
    with pytest.raises(CategoryNotFoundError):
        await repo.get_by_id(CategoryId("550e8400-e29b-41d4-a716-446655440099"))


@pytest.mark.asyncio
async def test_update_not_found(repo: InMemoryCategoryRepository) -> None:
    cat = Category.create(name="Ghost")
    with pytest.raises(CategoryNotFoundError):
        await repo.update(cat)


@pytest.mark.asyncio
async def test_list_all_and_children(repo: InMemoryCategoryRepository) -> None:
    parent = Category.create(name="Parent Cat")
    child = Category.create(name="Child Cat", parent_id=parent.id.value)
    await repo.add(parent)
    await repo.add(child)
    all_items = await repo.list_all(active_only=False)
    assert len(all_items) == 2
    children = await repo.list_children(parent.id)
    assert len(children) == 1
    assert children[0].name.value == "Child Cat"
