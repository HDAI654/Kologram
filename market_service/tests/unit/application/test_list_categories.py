from src.application.list_categories import (
    ListCategoriesHandler,
    ListCategoriesQuery,
)


class TestListCategories:
    async def test_returns_all_categories(self, uow, make_category):
        await uow.categories.add(make_category(name="Electronics"))
        await uow.categories.add(make_category(name="Furniture", is_active=False))

        result = await ListCategoriesHandler(uow).handle(ListCategoriesQuery())

        names = {item.name for item in result.items}
        assert names == {"Electronics", "Furniture"}

    async def test_active_only_filters_inactive(self, uow, make_category):
        await uow.categories.add(make_category(name="Electronics"))
        await uow.categories.add(make_category(name="Furniture", is_active=False))

        result = await ListCategoriesHandler(uow).handle(
            ListCategoriesQuery(active_only=True)
        )

        assert {item.name for item in result.items} == {"Electronics"}

    async def test_empty_when_no_categories(self, uow):
        result = await ListCategoriesHandler(uow).handle(ListCategoriesQuery())
        assert result.items == []

    async def test_parent_id_serialized_or_none(self, uow, make_category):
        parent = make_category(name="Electronics")
        await uow.categories.add(parent)
        child = make_category(name="Laptops", parent_id=parent.id.value)
        await uow.categories.add(child)

        result = await ListCategoriesHandler(uow).handle(ListCategoriesQuery())
        by_name = {item.name: item for item in result.items}

        assert by_name["Electronics"].parent_id is None
        assert by_name["Laptops"].parent_id == parent.id.value
