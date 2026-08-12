from shared.id_vo import ID
from src.exceptions import InvalidSessionIdError


class SessionId(ID):
    """UUID v4 identifier for an auth session."""

    def __init__(self, value: str) -> None:
        super().__init__(value, InvalidSessionIdError)
