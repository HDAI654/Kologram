import logging
from dataclasses import dataclass
from src.conf import Config
from src.domain.events.verification_token_created import VerificationTokenCreated
from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import EmailBlockedError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SendVerificationCommand:
    email: str


class SendVerificationHandler:
    """Store a verify-email token and emit VerificationTokenCreated on the bus."""

    def __init__(
        self,
        token_repository: VerificationTokenRepository,
        event_publisher: EventPublisher,
        email_blocklist: EmailBlocklistChecker,
    ) -> None:
        self._tokens = token_repository
        self._events = event_publisher
        self._blocklist = email_blocklist

    async def handle(self, command: SendVerificationCommand) -> None:
        logger.info("Creating email verification token")
        email = Email(command.email)

        if await self._blocklist.is_blocked(email):
            raise EmailBlockedError(f"Email '{command.email}' is blocked")

        token = VerificationToken.generate()
        await self._tokens.add(
            token=token,
            email=email,
            token_type="verifyemail",
            ttl_seconds=Config.VERIFY_EMAIL_EXPIRE_MINUTES * 60,
        )

        await self._events.publish(
            VerificationTokenCreated(
                token=token.value,
                email=email.value,
                token_type="verifyemail",
            )
        )
        logger.info("VerificationTokenCreated published email=%s", email.value)
