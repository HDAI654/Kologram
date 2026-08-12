import uuid
from typing import Self

from shared.base_vo import BaseVO
from src.exceptions import InvalidUserIdError


class UserId(BaseVO[str]):
    """UUID v4 identifier for a user (seller) reference."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidUserIdError(
                f"UserId must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidUserIdError("UserId must be a non-empty string")
        try:
            value = str(uuid.UUID(value, version=4))
        except Exception as exc:
            raise InvalidUserIdError(f"Invalid UUID v4 format: {value}") from exc
        super().__init__(value)

    @classmethod
    def generate(cls) -> Self:
        """Generate a new user identifier (test / fixture use)."""
        return cls(str(uuid.uuid4()))
