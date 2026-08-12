from shared.base_vo import BaseVO
from src.exceptions import InvalidLocationError

_MAX_LEN = 200


class Location(BaseVO[str]):
    """Free-form location label for a listing."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidLocationError(
                f"Location must be string, got {type(value).__name__}"
            )
        value = " ".join(value.split())
        if not value:
            raise InvalidLocationError("Location must be a non-empty string")
        if len(value) > _MAX_LEN:
            raise InvalidLocationError(
                f"Location must be at most {_MAX_LEN} characters"
            )
        super().__init__(value)
