from shared.id_vo import ID
from src.exceptions import InvalidVerificationTokenError


class VerificationToken(ID):
    """UUID v4 token stored in cache for verify-email and reset-password flows."""

    def __init__(self, value: str) -> None:
        super().__init__(value, InvalidVerificationTokenError)
