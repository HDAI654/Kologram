import re
from shared.base_vo import BaseVO
from src.exceptions import InvalidEmailError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Email(BaseVO[str]):
    """Normalized, validated email address."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidEmailError(f"Email must be string, got {type(value).__name__}")
        value = value.strip().lower()
        if not value:
            raise InvalidEmailError("Email must be a non-empty string")
        if not _EMAIL_RE.match(value) or len(value) > 254:
            raise InvalidEmailError("Invalid email address")
        super().__init__(value)
