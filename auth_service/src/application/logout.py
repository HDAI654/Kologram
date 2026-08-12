import logging
from dataclasses import dataclass
from src.domain.events.user_logged_out import UserLoggedOut
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class LogoutCommand:
    access_token: str
    device: str


class LogoutHandler:
    """Invalidate the current access-token session."""

    def __init__(
        self,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
        event_publisher: EventPublisher | None = None,
    ) -> None:
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder
        self._events = event_publisher

    async def handle(self, command: LogoutCommand) -> None:
        logger.info("Logout")
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

        # Reject already-revoked sessions (JWT may still be unexpired).
        await self._sessions.get_by_id(session_id)
        await self._sessions.delete(session_id=session_id, user_id=user_id)

        if self._events is not None:
            await self._events.publish(
                UserLoggedOut(
                    user_id=user_id.value,
                    session_id=session_id.value,
                    device=session_device.value,
                )
            )
        logger.info("Logout success: user_id=%s", user_id.value)
