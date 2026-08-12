import logging
from dataclasses import dataclass
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    DeviceMismatchError,
    PermissionDeniedError,
    SessionNotFoundError,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RevokeSessionCommand:
    access_token: str
    session_id: str
    device: str


class RevokeSessionHandler:
    """Delete one of the caller's sessions after validating the access token."""

    def __init__(
        self,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
    ) -> None:
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder

    async def handle(self, command: RevokeSessionCommand) -> None:
        logger.info("Revoke session: session_id=%s", command.session_id)
        payload = self._decoder.decode_and_validate(
            field_type_map=self._encoder.FIELD_TYPE_MAP,
            token=command.access_token,
            expected_token_type="access",
        )
        user_id = UserId(payload["sub"])
        current_session_id = SessionId(payload["sid"])
        current_device = Device(payload["dev"])

        try:
            await self._sessions.get_by_id(current_session_id)
        except SessionNotFoundError as exc:
            raise SessionNotFoundError(str(exc)) from exc

        if current_device.value != command.device:
            raise DeviceMismatchError("Session device mismatch")

        target = await self._sessions.get_by_id(SessionId(command.session_id))
        if target.user_id != user_id:
            raise PermissionDeniedError("Cannot revoke another user's session")

        await self._sessions.delete(session_id=target.id, user_id=user_id)
        logger.info("Session revoked: session_id=%s", command.session_id)
