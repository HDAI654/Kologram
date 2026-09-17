from datetime import datetime, timezone
from src.domain.entities.category import Category
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName


class TestCategory:
    def test_create_with_defaults(self):
        category = Category.create(name="Electronics")

        assert isinstance(category.id, CategoryId)
        assert isinstance(category.name, CategoryName)
        assert category.name.value == "Electronics"
        assert category.parent_id is None
        assert category.is_active is True
        assert isinstance(category.created_at, datetime)
        assert (datetime.now(timezone.utc) - category.created_at).total_seconds() < 1

    def test_create_with_all_fields(self):
        parent_id = CategoryId.generate()
        category_id = CategoryId.generate()
        created_at = datetime(2023, 1, 1, tzinfo=timezone.utc)

        category = Category.create(
            name="Laptops",
            parent_id=parent_id.value,
            id=category_id.value,
            is_active=False,
            created_at=created_at,
        )

        assert category.id == category_id
        assert category.name.value == "Laptops"
        assert category.parent_id == parent_id
        assert category.is_active is False
        assert category.created_at == created_at

    def test_rename(self):
        category = Category.create(name="Old Name")
        category.rename("New Name")
        assert category.name.value == "New Name"

    def test_activate(self):
        category = Category.create(name="Test", is_active=False)
        assert category.is_active is False
        category.activate()
        assert category.is_active is True

    def test_deactivate(self):
        category = Category.create(name="Test", is_active=True)
        assert category.is_active is True
        category.deactivate()
        assert category.is_active is False