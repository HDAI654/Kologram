from typing import Self

from shared.base_vo import BaseVO
from src.exceptions import InvalidListingStatusError

_ALLOWED = frozenset({"DRAFT", "ACTIVE", "SOLD", "EXPIRED", "CANCELLED", "SUSPENDED"})

# Valid transitions: from → set of allowed to-states
_TRANSITIONS: dict[str, frozenset[str]] = {
    "DRAFT": frozenset({"ACTIVE", "CANCELLED"}),
    "ACTIVE": frozenset({"SOLD", "EXPIRED", "CANCELLED", "SUSPENDED"}),
    "SOLD": frozenset(),
    "EXPIRED": frozenset({"ACTIVE", "CANCELLED"}),
    "CANCELLED": frozenset(),
    "SUSPENDED": frozenset({"ACTIVE", "CANCELLED"}),
}


class ListingStatus(BaseVO[str]):
    """Lifecycle status of a listing."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidListingStatusError(
                f"ListingStatus must be string, got {type(value).__name__}"
            )
        normalized = value.strip().upper()
        if normalized not in _ALLOWED:
            raise InvalidListingStatusError(f"Invalid listing status: {value}")
        super().__init__(normalized)

    @classmethod
    def draft(cls) -> Self:
        return cls("DRAFT")

    @classmethod
    def active(cls) -> Self:
        return cls("ACTIVE")

    @classmethod
    def sold(cls) -> Self:
        return cls("SOLD")

    @classmethod
    def expired(cls) -> Self:
        return cls("EXPIRED")

    @classmethod
    def cancelled(cls) -> Self:
        return cls("CANCELLED")

    @classmethod
    def suspended(cls) -> Self:
        return cls("SUSPENDED")

    def can_transition_to(self, target: "ListingStatus") -> bool:
        """Return True if moving from this status to ``target`` is allowed."""
        return target.value in _TRANSITIONS.get(self.value, frozenset())

    @property
    def is_editable(self) -> bool:
        """Listings in terminal or suspended states are not editable by sellers."""
        return self.value in {"DRAFT", "ACTIVE", "EXPIRED"}
