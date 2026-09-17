import pytest

from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import CategoryNotFoundError
from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryUnitOfWork,
)


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


class TestAdd:
    async def test_add_stores_category(self, uow, make_category):
        category = make_category(name="Electronics")

        await uow.categories.add(category)

        assert await uow.categories.get_by_id(category.id) is category


class TestGetById:
    async def test_returns_stored_category(self, uow, make_category):
        category = make_category(name="Electronics")
        await uow.categories.add(category)

        assert await uow.categories.get_by_id(category.id) is category

    async def test_raises_when_missing(self, uow):
        with pytest.raises(CategoryNotFoundError):
            await uow.categories.get_by_id(CategoryId.generate())


class TestGetByName:
    async def test_returns_matching_category(self, uow, make_category):
        category = make_category(name="Electronics")
        await uow.categories.add(category)

        result = await uow.categories.get_by_name(CategoryName("Electronics"))

        assert result is category

    async def test_returns_none_when_missing(self, uow):
        assert await uow.categories.get_by_name(CategoryName("Nope")) is None

    async def test_name_matching_is_value_based(self, uow, make_category):
        category = make_category(name="Electronics")
        await uow.categories.add(category)

        # Distinct VO instance, equal value.
        assert await uow.categories.get_by_name(CategoryName("Electronics")) is category


class TestUpdate:
    async def test_persists_changes(self, uow, make_category):
        category = make_category(name="Electronics")
        await uow.categories.add(category)

        category.rename("Consumer Electronics")
        await uow.categories.update(category)

        stored = await uow.categories.get_by_id(category.id)
        assert stored.name.value == "Consumer Electronics"

    async def test_missing_raises(self, uow, make_category):
        with pytest.raises(CategoryNotFoundError):
            await uow.categories.update(make_category())


class TestListAll:
    async def test_sorted_by_name(self, uow, make_category):
        await uow.categories.add(make_category(name="Zebra"))
        await uow.categories.add(make_category(name="Apple"))

        names = [c.name.value for c in await uow.categories.list_all()]

        assert names == ["Apple", "Zebra"]

    async def test_active_only_filters_inactive(self, uow, make_category):
        await uow.categories.add(make_category(name="Active"))
        await uow.categories.add(make_category(name="Inactive", is_active=False))

        names = [c.name.value for c in await uow.categories.list_all(active_only=True)]

        assert names == ["Active"]

    async def test_empty(self, uow):
        assert await uow.categories.list_all() == []


class TestListChildren:
    async def test_returns_children(self, uow, make_category):
        parent = make_category(name="Root Category")
        child_a = make_category(name="Leaf Alpha", parent_id=parent.id.value)
        child_b = make_category(name="Leaf Beta", parent_id=parent.id.value)
        other = make_category(name="Unrelated")
        await uow.categories.add(parent)
        await uow.categories.add(child_a)
        await uow.categories.add(child_b)
        await uow.categories.add(other)

        children = await uow.categories.list_children(parent.id)

        ids = {c.id for c in children}
        assert ids == {child_a.id, child_b.id}

    async def test_empty_when_no_children(self, uow, make_category):
        parent = make_category(name="Root Category")
        await uow.categories.add(parent)

        assert await uow.categories.list_children(parent.id) == []
