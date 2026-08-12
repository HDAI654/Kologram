from typing import Self
from shared.base_vo import BaseVO
from src.exceptions import InvalidUserStatusError

_ALLOWED = frozenset({"ACTIVE", "SUSPENDED"})


class UserStatus(BaseVO[str]):
    """Represents the current status of a user account."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidUserStatusError(
                f"UserStatus must be a string, got {type(value).__name__}"
            )

        normalized = value.strip().upper()
        if normalized not in _ALLOWED:
            raise InvalidUserStatusError(
                f"Invalid user status: {value!r}. "
                f"Expected one of: {', '.join(sorted(_ALLOWED))}."
            )

        super().__init__(normalized)

    @classmethod
    def active(cls) -> Self:
        """Create an active user status."""
        return cls("ACTIVE")

    @classmethod
    def suspended(cls) -> Self:
        """Create a suspended user status."""
        return cls("SUSPENDED")

    @property
    def is_active(self) -> bool:
        """Return whether the user account is currently active."""
        return self.value == "ACTIVE"
