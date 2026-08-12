from datetime import date
from shared.entity import Entity
from src.domain.value_objects.date import Date
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId


class Session(Entity):
    """Active login session bound to a user and device."""

    def __init__(
        self,
        id: SessionId,
        user_id: UserId,
        device: Device,
        created_at: Date,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.device = device
        self.created_at = created_at
        super().__init__()

    @classmethod
    def create(
        cls,
        user_id: str,
        device: str = "unknown",
        *,
        id: str | None = None,
        created_at: str | date | None = None,
    ) -> "Session":
        """Factory for a new session."""
        return cls(
            id=SessionId(id) if id is not None else SessionId.generate(),
            user_id=UserId(user_id),
            device=Device(device),
            created_at=(
                Date(created_at) if created_at is not None else Date(date.today())
            ),
        )
