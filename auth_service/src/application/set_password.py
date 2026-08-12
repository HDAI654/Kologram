import logging
from dataclasses import dataclass
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.value_objects.device import Device
from src.domain.value_objects.password import Password
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SetPasswordCommand:
    access_token: str
    new_password: str
    device: str


class SetPasswordHandler:
    """Update password and revoke other sessions."""

    def __init__(
        self,
        uow: UnitOfWork,
        session_repository: SessionRepository,
        token_decoder: TokenDecoder,
        token_encoder: TokenEncoder,
        password_hasher: PasswordHasher,
    ) -> None:
        self._uow = uow
        self._sessions = session_repository
        self._decoder = token_decoder
        self._encoder = token_encoder
        self._hasher = password_hasher

    async def handle(self, command: SetPasswordCommand) -> None:
        logger.info("Set password")
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

        password = Password(command.new_password)
        hashed = self._hasher.hash(password)

        async with self._uow:
            await self._uow.users.update(user_id, new_password=hashed)
            await self._uow.commit()

        await self._sessions.delete_all_other_sessions(
            current_session_id=session_id, user_id=user_id
        )

        logger.info("Password changed: user_id=%s", user_id.value)
