from shared.id_vo import ID
from src.exceptions import InvalidUserIdError


class UserId(ID):
    """UUID v4 identifier for a user aggregate."""

    def __init__(self, value: str) -> None:
        super().__init__(value, InvalidUserIdError)
