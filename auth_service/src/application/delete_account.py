import logging
from dataclasses import dataclass
from src.domain.events.account_deleted import AccountDeleted
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DeleteAccountCommand:
    access_token: str
    device: str


class DeleteAccountHandler:
    """Delete user aggregate and all sessions after token validation."""

    def __init__(
        self,
        uow: UnitOfWork,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._uow = uow
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder
        self._events = event_publisher

    async def handle(self, command: DeleteAccountCommand) -> None:
        logger.info("Delete account")
        payload = self._decoder.decode_and_validate(
            field_type_map=self._encoder.FIELD_TYPE_MAP,
            token=command.access_token,
            expected_token_type="access",
        )
        user_id = UserId(payload["sub"])
        session_id = SessionId(payload["sid"])
        session_device = Device(payload["dev"])

        if session_device.value != command.device:
            raise DeviceMismatchError("Session device mismatch")

        await self._sessions.get_by_id(session_id)

        async with self._uow:
            await self._uow.users.delete(user_id)
            await self._uow.commit()

        await self._sessions.delete(session_id=session_id, user_id=user_id)
        await self._sessions.delete_all_other_sessions(
            current_session_id=session_id, user_id=user_id
        )

        if self._events is not None:
            await self._events.publish(AccountDeleted(user_id=user_id.value))

        logger.info("Account deleted: user_id=%s", user_id.value)
