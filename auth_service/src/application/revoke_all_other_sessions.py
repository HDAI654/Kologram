import logging
from dataclasses import dataclass
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RevokeAllOtherSessionsCommand:
    access_token: str
    device: str


class RevokeAllOtherSessionsHandler:
    """Keep only the session embedded in the access token."""

    def __init__(
        self,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
    ) -> None:
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder

    async def handle(self, command: RevokeAllOtherSessionsCommand) -> None:
        logger.info("Revoke all other sessions")
        payload = self._decoder.decode_and_validate(
            field_type_map=self._encoder.FIELD_TYPE_MAP,
            token=command.access_token,
            expected_token_type="access",
        )
        user_id = UserId(payload["sub"])
        session_id = SessionId(payload["sid"])
        session_device = Device(payload["dev"])

        await self._sessions.get_by_id(session_id)
        if session_device.value != command.device:
            raise DeviceMismatchError("Session device mismatch")

        await self._sessions.delete_all_other_sessions(
            current_session_id=session_id, user_id=user_id
        )
        logger.info("Other sessions revoked: user_id=%s", user_id.value)
