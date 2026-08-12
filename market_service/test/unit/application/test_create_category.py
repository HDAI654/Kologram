import pytest

from src.application.create_category import CreateCategoryCommand, CreateCategoryHandler
from src.domain.entities.category import Category
from src.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.mark.asyncio
async def test_create_category_success(uow: InMemoryUnitOfWork) -> None:
    handler = CreateCategoryHandler(uow, NoOpEventPublisher())
    result = await handler.handle(CreateCategoryCommand(name="Home & Garden"))
    assert result.name == "Home & Garden"
    assert result.is_active is True
    assert result.parent_id is None


@pytest.mark.asyncio
async def test_create_category_duplicate(uow: InMemoryUnitOfWork) -> None:
    handler = CreateCategoryHandler(uow, NoOpEventPublisher())
    await handler.handle(CreateCategoryCommand(name="Sports"))
    with pytest.raises(CategoryAlreadyExistsError):
        await handler.handle(CreateCategoryCommand(name="Sports"))


@pytest.mark.asyncio
async def test_create_category_with_parent(uow: InMemoryUnitOfWork) -> None:
    parent = Category.create(name="Electronics")
    async with uow:
        await uow.categories.add(parent)
        await uow.commit()

    handler = CreateCategoryHandler(uow, NoOpEventPublisher())
    result = await handler.handle(
        CreateCategoryCommand(name="Phones", parent_id=parent.id.value)
    )
    assert result.parent_id == parent.id.value


@pytest.mark.asyncio
async def test_create_category_missing_parent(uow: InMemoryUnitOfWork) -> None:
    handler = CreateCategoryHandler(uow, NoOpEventPublisher())
    with pytest.raises(CategoryNotFoundError):
        await handler.handle(
            CreateCategoryCommand(
                name="Orphan",
                parent_id="550e8400-e29b-41d4-a716-446655440099",
            )
        )
