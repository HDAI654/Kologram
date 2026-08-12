from shared.base_vo import BaseVO
from src.exceptions import InvalidDescriptionError

_MAX_LEN = 5000


class Description(BaseVO[str]):
    """Validated listing description (may be empty)."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidDescriptionError(
                f"Description must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if len(value) > _MAX_LEN:
            raise InvalidDescriptionError(
                f"Description must be at most {_MAX_LEN} characters"
            )
        super().__init__(value)
