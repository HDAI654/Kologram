import logging
from dataclasses import dataclass
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.verification_token import VerificationToken
from src.domain.value_objects.password import Password
from src.exceptions import (
    InvalidVerificationTokenError,
    InvalidVerificationTokenError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ResetPasswordCommand:
    verify_token: str
    new_password: str


class ResetPasswordHandler:
    """Validate reset token and update the user password hash."""

    def __init__(
        self,
        uow: UnitOfWork,
        password_hasher: PasswordHasher,
        token_repository: VerificationTokenRepository,
    ) -> None:
        self._uow = uow
        self._hasher = password_hasher
        self._tokens = token_repository

    async def handle(self, command: ResetPasswordCommand) -> None:
        logger.info("Reset password")

        try:
            token_vo = VerificationToken(command.verify_token)
        except InvalidVerificationTokenError as exc:
            raise InvalidVerificationTokenError(
                f"Token '{command.verify_token}' not found"
            ) from exc

        email = await self._tokens.get(token_vo, "forget_pass_verify")
        if email is None:
            raise InvalidVerificationTokenError(
                f"Token '{command.verify_token}' not found"
            )

        password = Password(command.new_password)
        hashed = self._hasher.hash(password)

        async with self._uow:
            user = await self._uow.users.get_by_email(email)
            await self._uow.users.update(user.id, new_password=hashed)
            await self._uow.commit()

        # Consume token only after password is persisted.
        await self._tokens.delete(token_vo, "forget_pass_verify")

        logger.info("Password reset: user_id=%s", user.id.value)
