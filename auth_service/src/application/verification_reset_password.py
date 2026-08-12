import logging
from dataclasses import dataclass
from src.conf import Config
from src.domain.events.verification_token_created import VerificationTokenCreated
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.email_verification_token import EmailVerificationToken

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class VerificationResetPassCommand:
    email: str


class VerificationResetPassHandler:
    """Create reset token and publish event when the email is registered.

    Unknown emails are a silent no-op so callers cannot enumerate accounts.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        token_repository: VerificationTokenRepository,
        event_publisher: EventPublisher,
    ) -> None:
        self._uow = uow
        self._tokens = token_repository
        self._events = event_publisher

    async def handle(self, command: VerificationResetPassCommand) -> None:
        logger.info("Forget-password requested")
        email = Email(command.email)

        # SECURITY: do not reveal whether the email is registered.
        async with self._uow:
            exists = await self._uow.users.exists_by_email(email)
        if not exists:
            logger.info("Forget-password for unknown email (no-op)")
            return

        token = EmailVerificationToken.generate()
        await self._tokens.add(
            token=token,
            email=email,
            token_type="forget_pass_verify",
            ttl_seconds=Config.RESET_PASSWORD_EXPIRE_MINUTES * 60,
        )

        await self._events.publish(
            VerificationTokenCreated(
                token=token.value,
                email=email.value,
                token_type="forget_pass_verify",
            )
        )
        logger.info("VerificationTokenCreated published (reset) email=%s", email.value)
