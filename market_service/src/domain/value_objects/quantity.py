from shared.base_vo import BaseVO
from src.exceptions import InvalidQuantityError


class Quantity(BaseVO[int]):
    """Positive integer quantity available for a listing."""

    def __init__(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidQuantityError(
                f"Quantity must be int, got {type(value).__name__}"
            )
        if value < 0:
            raise InvalidQuantityError("Quantity must be non-negative")
        if value > 1_000_000:
            raise InvalidQuantityError("Quantity exceeds maximum allowed")
        super().__init__(value)
