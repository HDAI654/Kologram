from abc import ABC, abstractmethod
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId


class TokenEncoder(ABC):
    """Creates signed access and refresh tokens."""

    FIELD_TYPE_MAP: dict

    @abstractmethod
    def create_access_token(
        self,
        user_id: UserId,
        session_id: SessionId,
        device: Device,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def create_refresh_token(
        self,
        user_id: UserId,
        session_id: SessionId,
        device: Device,
    ) -> str:
        raise NotImplementedError
