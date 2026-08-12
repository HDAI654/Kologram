from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.email_verification_token import EmailVerificationToken


class InMemoryVerificationTokenRepository(VerificationTokenRepository):
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    async def add(
        self,
        token: EmailVerificationToken,
        email: Email,
        token_type: str,
        ttl_seconds: int,
    ) -> None:
        self._store[(token_type, token.value)] = email.value

    async def get(
        self,
        token: EmailVerificationToken,
        token_type: str,
    ) -> Email | None:
        raw = self._store.get((token_type, token.value))
        return Email(raw) if raw is not None else None

    async def delete(
        self,
        token: EmailVerificationToken,
        token_type: str,
    ) -> None:
        self._store.pop((token_type, token.value), None)
