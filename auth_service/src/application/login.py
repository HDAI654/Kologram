import logging
from dataclasses import dataclass
from src.domain.entities.session import Session
from src.domain.events.user_logged_in import UserLoggedIn
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.email import Email
from src.exceptions import InvalidEmailOrPasswordError, UserNotFoundError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str
    device: str


@dataclass(frozen=True, slots=True)
class LoginResult:
    access_token: str
    refresh_token: str


class LoginHandler:
    """Authenticate credentials and issue USER-role tokens."""

    def __init__(
        self,
        uow: UnitOfWork,
        session_repository: SessionRepository,
        token_encoder: TokenEncoder,
        password_hasher: PasswordHasher,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._sessions = session_repository
        self._tokens = token_encoder
        self._hasher = password_hasher
        self._events = event_publisher

    async def handle(self, command: LoginCommand) -> LoginResult:
        logger.info("Login attempt: email=%s", command.email)
        email = Email(command.email)
        try:
            async with self._uow:
                user = await self._uow.users.get_by_email(email)
        except UserNotFoundError as exc:
            raise InvalidEmailOrPasswordError() from exc

        # SECURITY: login only verifies hash — no strength rules on existing passwords.
        if not self._hasher.verify(command.password, user.hashed_password):
            raise InvalidEmailOrPasswordError()

        session = Session.create(user_id=user.id.value, device=command.device)
        await self._sessions.add(session)

        access = self._tokens.create_access_token(user.id, session.id, session.device)
        refresh = self._tokens.create_refresh_token(user.id, session.id, session.device)

        if self._events is not None:
            await self._events.publish(
                UserLoggedIn(
                    user_id=user.id.value,
                    email=user.email.value,
                    session_id=session.id.value,
                    device=session.device.value,
                )
            )

        logger.info("Login success: user_id=%s", user.id.value)
        return LoginResult(access_token=access, refresh_token=refresh)
