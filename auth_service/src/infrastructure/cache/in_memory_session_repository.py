import logging
from datetime import date
from src.domain.entities.session import Session
from src.domain.ports.session_repository import SessionRepository
from src.domain.value_objects.date import Date
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import SessionNotFoundError

logger = logging.getLogger(__name__)


class InMemorySessionRepository(SessionRepository):
    def __init__(self) -> None:
        self._by_id: dict[str, Session] = {}
        self._by_user: dict[str, set[str]] = {}

    async def add(self, session: Session) -> None:
        self._by_id[session.id.value] = session
        self._by_user.setdefault(session.user_id.value, set()).add(session.id.value)

    async def get_by_id(self, session_id: SessionId) -> Session:
        session = self._by_id.get(session_id.value)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id.value}' not found")
        return session

    async def delete(self, session_id: SessionId, user_id: UserId) -> None:
        self._by_id.pop(session_id.value, None)
        user_set = self._by_user.get(user_id.value)
        if user_set is not None:
            user_set.discard(session_id.value)

    async def delete_all_other_sessions(
        self,
        current_session_id: SessionId,
        user_id: UserId,
    ) -> None:
        ids = list(self._by_user.get(user_id.value, set()))
        for sid in ids:
            if sid != current_session_id.value:
                self._by_id.pop(sid, None)
                self._by_user[user_id.value].discard(sid)

    async def extend_session(self, session_id: SessionId) -> None:
        session = await self.get_by_id(session_id)
        # Touch created_at metadata — TTL is owned by Redis adapter in prod.
        session.created_at = Date(date.today())
