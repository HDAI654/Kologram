import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from src.conf import Config
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RotateTokensCommand:
    refresh_token: str
    device: str


@dataclass(frozen=True, slots=True)
class RotateTokensResult:
    access_token: str
    refresh_token: str | None


class RotateTokensHandler:
    """Issue a new access token; rotate refresh when near expiry."""

    def __init__(
        self,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
    ) -> None:
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder

    async def handle(self, command: RotateTokensCommand) -> RotateTokensResult:
        logger.info("Rotate tokens")
        payload = self._decoder.decode_and_validate(
            field_type_map=self._encoder.FIELD_TYPE_MAP,
            token=command.refresh_token,
            expected_token_type="refresh",
        )
        user_id = UserId(payload["sub"])
        session_id = SessionId(payload["sid"])
        session_device = Device(payload["dev"])

        if session_device.value != command.device:
            raise DeviceMismatchError("Session device mismatch")

        # SECURITY: do not mint tokens for revoked sessions.
        await self._sessions.get_by_id(session_id)

        access = self._encoder.create_access_token(user_id, session_id, session_device)

        need_refresh = False
        try:
            exp = float(payload["exp"])
            exp_dt = datetime.fromtimestamp(exp, timezone.utc)
            threshold = timedelta(minutes=Config.ROTATE_THRESHOLD_MINUTES)
            need_refresh = exp_dt - datetime.now(timezone.utc) <= threshold
        except Exception:
            need_refresh = False

        if need_refresh:
            await self._sessions.extend_session(session_id)
            refresh = self._encoder.create_refresh_token(
                user_id, session_id, session_device
            )
            return RotateTokensResult(access_token=access, refresh_token=refresh)

        return RotateTokensResult(access_token=access, refresh_token=None)
