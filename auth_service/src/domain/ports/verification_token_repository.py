"""One-time email verification token port."""

from abc import ABC, abstractmethod

from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken


class VerificationTokenRepository(ABC):
    """Stores short-lived verify-email / reset-password tokens (cache)."""

    @abstractmethod
    async def add(
        self,
        token: VerificationToken,
        email: Email,
        token_type: str,
        ttl_seconds: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        token: VerificationToken,
        token_type: str,
    ) -> Email | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(
        self,
        token: VerificationToken,
        token_type: str,
    ) -> None:
        raise NotImplementedError
