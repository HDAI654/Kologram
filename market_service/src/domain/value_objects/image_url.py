from shared.base_vo import BaseVO
from src.exceptions import InvalidImageUrlError

_MAX_LEN = 2048


class ImageUrl(BaseVO[str]):
    """Validated absolute or relative image URL."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidImageUrlError(
                f"ImageUrl must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidImageUrlError("ImageUrl must be a non-empty string")
        if len(value) > _MAX_LEN:
            raise InvalidImageUrlError(
                f"ImageUrl must be at most {_MAX_LEN} characters"
            )
        if not (
            value.startswith("http://")
            or value.startswith("https://")
            or value.startswith("/")
        ):
            raise InvalidImageUrlError("ImageUrl must start with http(s):// or /")
        super().__init__(value)
