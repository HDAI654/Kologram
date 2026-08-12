import uuid
from typing import Self

from shared.base_vo import BaseVO
from src.exceptions import InvalidListingIdError


class ListingId(BaseVO[str]):
    """UUID v4 identifier for a listing aggregate."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidListingIdError(
                f"ListingId must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidListingIdError("ListingId must be a non-empty string")
        try:
            value = str(uuid.UUID(value, version=4))
        except Exception as exc:
            raise InvalidListingIdError(f"Invalid UUID v4 format: {value}") from exc
        super().__init__(value)

    @classmethod
    def generate(cls) -> Self:
        """Generate a new listing identifier."""
        return cls(str(uuid.uuid4()))
