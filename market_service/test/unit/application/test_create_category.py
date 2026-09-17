import pytest
from uuid import uuid4
from src.application.create_category import (
    CreateCategoryCommand,
    CreateCategoryHandler,
)
from src.domain.events.category_created import CategoryCreated
from src.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError


class TestCreateCategory:
    async def test_creates_top_level_category(self, uow, event_publisher):
        handler = CreateCategoryHandler(uow, event_publisher)

        result = await handler.handle(CreateCategoryCommand(name="Electronics"))

        assert result.name == "Electronics"
        assert result.parent_id is None
        assert result.is_active is True
        assert uow.committed is True
        assert len(uow.categories.added) == 1

        assert len(event_publisher.published) == 1
        event = event_publisher.published[0]
        assert isinstance(event, CategoryCreated)
        assert event.category_id == result.category_id
        assert event.name == "Electronics"
        assert event.parent_id is None

    async def test_creates_child_category_when_parent_exists(
        self, uow, event_publisher, make_category
    ):
        parent = make_category(name="Electronics")
        await uow.categories.add(parent)
        handler = CreateCategoryHandler(uow, event_publisher)

        result = await handler.handle(
            CreateCategoryCommand(name="Laptops", parent_id=parent.id.value)
        )

        assert result.parent_id == parent.id.value
        assert event_publisher.published[0].parent_id == parent.id.value

    async def test_duplicate_name_raises_and_does_not_commit(
        self, uow, event_publisher, make_category
    ):
        existing = make_category(name="Electronics")
        await uow.categories.add(existing)
        handler = CreateCategoryHandler(uow, event_publisher)

        with pytest.raises(CategoryAlreadyExistsError):
            await handler.handle(CreateCategoryCommand(name="Electronics"))

        assert uow.committed is False
        assert uow.rolled_back is True
        assert event_publisher.published == []

    async def test_missing_parent_raises_category_not_found(
        self, uow, event_publisher
    ):
        handler = CreateCategoryHandler(uow, event_publisher)
        with pytest.raises(CategoryNotFoundError):
            await handler.handle(
                CreateCategoryCommand(
                    name="Laptops",
                    parent_id=str(uuid4()),
                )
            )
        assert uow.committed is False

    async def test_invalid_name_is_rejected_by_domain_before_uow_use(
        self, uow, event_publisher
    ):
        from src.exceptions import InvalidCategoryNameError

        handler = CreateCategoryHandler(uow, event_publisher)
        with pytest.raises(InvalidCategoryNameError):
            await handler.handle(CreateCategoryCommand(name="a"))
        # Name validation happens before entering the UoW.
        assert uow.entered is False
        assert uow.committed is False

    async def test_without_event_publisher_still_commits(self, uow):
        handler = CreateCategoryHandler(uow, event_publisher=None)
        result = await handler.handle(CreateCategoryCommand(name="Books"))
        assert result.name == "Books"
        assert uow.committed is True