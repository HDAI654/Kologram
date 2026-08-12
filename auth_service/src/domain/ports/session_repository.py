from abc import ABC, abstractmethod
from src.domain.entities.session import Session
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId


class SessionRepository(ABC):
    """Port for session lifecycle."""

    @abstractmethod
    async def add(self, session: Session) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, session_id: SessionId) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: SessionId, user_id: UserId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_all_other_sessions(
        self,
        current_session_id: SessionId,
        user_id: UserId,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def extend_session(self, session_id: SessionId) -> None:
        raise NotImplementedError
