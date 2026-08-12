import logging
from dataclasses import dataclass

from src.domain.ports.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ListCategoriesQuery:
    active_only: bool = False


@dataclass(frozen=True, slots=True)
class CategoryItem:
    category_id: str
    name: str
    parent_id: str | None
    is_active: bool
    created_at: str


@dataclass(frozen=True, slots=True)
class ListCategoriesResult:
    items: list[CategoryItem]


class ListCategoriesHandler:
    """Return the category tree (flat list)."""

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def handle(self, query: ListCategoriesQuery) -> ListCategoriesResult:
        async with self._uow:
            categories = await self._uow.categories.list_all(
                active_only=query.active_only
            )

        items = [
            CategoryItem(
                category_id=c.id.value,
                name=c.name.value,
                parent_id=c.parent_id.value if c.parent_id else None,
                is_active=c.is_active,
                created_at=c.created_at.isoformat(),
            )
            for c in categories
        ]
        return ListCategoriesResult(items=items)
