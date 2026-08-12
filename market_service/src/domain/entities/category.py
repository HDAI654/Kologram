from datetime import datetime, timezone

from shared.entity import Entity
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName


class Category(Entity):
    """Category aggregate root — taxonomy node for listings."""

    def __init__(
        self,
        id: CategoryId,
        name: CategoryName,
        parent_id: CategoryId | None,
        is_active: bool,
        created_at: datetime,
    ) -> None:
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.is_active = is_active
        self.created_at = created_at
        super().__init__()

    @classmethod
    def create(
        cls,
        name: str,
        *,
        parent_id: str | None = None,
        id: str | None = None,
        is_active: bool = True,
        created_at: datetime | None = None,
    ) -> "Category":
        """Factory for a new category."""
        return cls(
            id=CategoryId(id) if id is not None else CategoryId.generate(),
            name=CategoryName(name),
            parent_id=CategoryId(parent_id) if parent_id is not None else None,
            is_active=is_active,
            created_at=created_at or datetime.now(timezone.utc),
        )

    def rename(self, name: str) -> None:
        """Change display name."""
        self.name = CategoryName(name)

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
