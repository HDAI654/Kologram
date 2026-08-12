from abc import ABC, abstractmethod

from src.domain.entities.category import Category
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName


class CategoryRepository(ABC):
    """Port for category aggregate persistence."""

    @abstractmethod
    async def add(self, category: Category) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: CategoryId) -> Category:
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: CategoryName) -> Category | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, category: Category) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, *, active_only: bool = False) -> list[Category]:
        raise NotImplementedError

    @abstractmethod
    async def list_children(self, parent_id: CategoryId) -> list[Category]:
        raise NotImplementedError
