import pytest

from src.application.create_category import CreateCategoryCommand, CreateCategoryHandler
from src.application.list_categories import ListCategoriesHandler, ListCategoriesQuery
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher
from src.infrastructure.persistence.in_memory_unit_of_work import InMemoryUnitOfWork


@pytest.fixture
def uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.mark.asyncio
async def test_list_categories(uow: InMemoryUnitOfWork) -> None:
    await CreateCategoryHandler(uow, NoOpEventPublisher()).handle(
        CreateCategoryCommand(name="Books")
    )
    await CreateCategoryHandler(uow, NoOpEventPublisher()).handle(
        CreateCategoryCommand(name="Toys")
    )
    result = await ListCategoriesHandler(uow).handle(
        ListCategoriesQuery(active_only=True)
    )
    names = {i.name for i in result.items}
    assert "Books" in names
    assert "Toys" in names
