import logging
from dataclasses import dataclass
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.domain.events.user_registered import UserRegistered
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.verification_token import VerificationToken
from src.domain.value_objects.password import Password
from src.exceptions import (
    InvalidVerificationTokenError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SignupCommand:
    verify_token: str
    password: str
    device: str


@dataclass(frozen=True, slots=True)
class SignupResult:
    access_token: str
    refresh_token: str


class SignupHandler:
    """Consume verify-email token, create user + session, issue USER tokens."""

    def __init__(
        self,
        uow: UnitOfWork,
        session_repository: SessionRepository,
        token_encoder: TokenEncoder,
        password_hasher: PasswordHasher,
        token_repository: VerificationTokenRepository,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._sessions = session_repository
        self._tokens = token_encoder
        self._hasher = password_hasher
        self._verify_tokens = token_repository
        self._events = event_publisher

    async def handle(self, command: SignupCommand) -> SignupResult:
        logger.info("Signing up user")

        try:
            token_vo = VerificationToken(command.verify_token)
        except InvalidVerificationTokenError as exc:
            raise InvalidVerificationTokenError(
                f"Token '{command.verify_token}' not found"
            ) from exc

        email = await self._verify_tokens.get(token_vo, "verifyemail")
        if email is None:
            raise InvalidVerificationTokenError(
                f"Token '{command.verify_token}' not found"
            )

        password = Password(command.password)
        hashed = self._hasher.hash(password)

        async with self._uow:
            user = User.create(email=email.value, hashed_password=hashed.value)
            await self._uow.users.add(user)
            await self._uow.commit()

        # Only consume the one-time token after the user row is durable.
        await self._verify_tokens.delete(token_vo, "verifyemail")

        session = Session.create(user_id=user.id.value, device=command.device)
        await self._sessions.add(session)

        access = self._tokens.create_access_token(
            user.id,
            session.id,
            session.device,
        )
        refresh = self._tokens.create_refresh_token(
            user.id,
            session.id,
            session.device,
        )

        if self._events is not None:
            await self._events.publish(
                UserRegistered(user_id=user.id.value, email=user.email.value)
            )

        logger.info("User signed up: user_id=%s", user.id.value)
        return SignupResult(access_token=access, refresh_token=refresh)
