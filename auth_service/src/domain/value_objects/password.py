import re
from shared.base_vo import BaseVO
from src.exceptions import InvalidPasswordError

_MIN_LEN = 8
_MAX_LEN = 128


class Password(BaseVO[str]):
    """Validated plain password used before hashing."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidPasswordError(
                f"Password must be string, got {type(value).__name__}"
            )
        if not (_MIN_LEN <= len(value) <= _MAX_LEN):
            raise InvalidPasswordError(
                f"Password length must be between {_MIN_LEN} and {_MAX_LEN}"
            )
        if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
            raise InvalidPasswordError(
                "Password must contain at least one letter and one digit"
            )
        super().__init__(value)
