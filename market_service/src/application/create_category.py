import logging
from dataclasses import dataclass

from src.domain.entities.category import Category
from src.domain.events.category_created import CategoryCreated
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import CategoryAlreadyExistsError, CategoryNotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateCategoryCommand:
    name: str
    parent_id: str | None = None


@dataclass(frozen=True, slots=True)
class CreateCategoryResult:
    category_id: str
    name: str
    parent_id: str | None
    is_active: bool


class CreateCategoryHandler:
    """Create a new category in the taxonomy."""

    def __init__(
        self,
        uow: UnitOfWork,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._events = event_publisher

    async def handle(self, command: CreateCategoryCommand) -> CreateCategoryResult:
        logger.info("Creating category name=%s", command.name)
        name_vo = CategoryName(command.name)

        async with self._uow:
            existing = await self._uow.categories.get_by_name(name_vo)
            if existing is not None:
                raise CategoryAlreadyExistsError(
                    f"Category '{command.name}' already exists"
                )

            if command.parent_id is not None:
                try:
                    await self._uow.categories.get_by_id(CategoryId(command.parent_id))
                except CategoryNotFoundError as exc:
                    raise CategoryNotFoundError(
                        f"Parent category '{command.parent_id}' not found"
                    ) from exc

            category = Category.create(
                name=command.name,
                parent_id=command.parent_id,
            )
            await self._uow.categories.add(category)
            await self._uow.commit()

        if self._events is not None:
            await self._events.publish(
                CategoryCreated(
                    category_id=category.id.value,
                    name=category.name.value,
                    parent_id=category.parent_id.value if category.parent_id else None,
                )
            )

        logger.info("Category created id=%s", category.id.value)
        return CreateCategoryResult(
            category_id=category.id.value,
            name=category.name.value,
            parent_id=category.parent_id.value if category.parent_id else None,
            is_active=category.is_active,
        )
