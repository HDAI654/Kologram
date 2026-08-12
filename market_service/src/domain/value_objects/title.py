from shared.base_vo import BaseVO
from src.exceptions import InvalidTitleError

_MIN_LEN = 3
_MAX_LEN = 120


class Title(BaseVO[str]):
    """Validated listing title."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidTitleError(f"Title must be string, got {type(value).__name__}")
        value = " ".join(value.split())
        if not (_MIN_LEN <= len(value) <= _MAX_LEN):
            raise InvalidTitleError(
                f"Title length must be between {_MIN_LEN} and {_MAX_LEN}"
            )
        super().__init__(value)
