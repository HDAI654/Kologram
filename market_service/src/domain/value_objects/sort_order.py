from shared.base_vo import BaseVO
from src.exceptions import InvalidSortOrderError


class SortOrder(BaseVO[int]):
    """Non-negative integer used to order listing images."""

    def __init__(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise InvalidSortOrderError(
                f"SortOrder must be int, got {type(value).__name__}"
            )
        if value < 0:
            raise InvalidSortOrderError("SortOrder must be non-negative")
        if value > 1000:
            raise InvalidSortOrderError("SortOrder exceeds maximum allowed")
        super().__init__(value)
