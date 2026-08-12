from shared.base_vo import BaseVO
from src.exceptions import InvalidHashedPasswordError


class HashedPassword(BaseVO[str]):
    """Opaque password hash string produced by PasswordHasher."""

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise InvalidHashedPasswordError(
                f"HashedPassword must be string, got {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise InvalidHashedPasswordError("HashedPassword must be non-empty")
        super().__init__(value)
