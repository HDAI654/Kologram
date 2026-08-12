from shared.base_vo import BaseVO
from src.exceptions import InvalidCategoryNameError

_MIN_LEN = 2
_MAX_LEN = 80


class CategoryName(BaseVO[str]):
    """Validated category display name."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidCategoryNameError(
                f"CategoryName must be string, got {type(value).__name__}"
            )
        value = " ".join(value.split())
        if not (_MIN_LEN <= len(value) <= _MAX_LEN):
            raise InvalidCategoryNameError(
                f"Category name length must be between {_MIN_LEN} and {_MAX_LEN}"
            )
        super().__init__(value)
