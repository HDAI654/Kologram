import uuid
from typing import Self

from shared.base_vo import BaseVO
from src.exceptions import InvalidCategoryIdError


class CategoryId(BaseVO[str]):
    """UUID v4 identifier for a category aggregate."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidCategoryIdError(
                f"CategoryId must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidCategoryIdError("CategoryId must be a non-empty string")
        try:
            value = str(uuid.UUID(value, version=4))
        except Exception as exc:
            raise InvalidCategoryIdError(f"Invalid UUID v4 format: {value}") from exc
        super().__init__(value)

    @classmethod
    def generate(cls) -> Self:
        """Generate a new category identifier."""
        return cls(str(uuid.uuid4()))
