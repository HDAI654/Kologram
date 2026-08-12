from dataclasses import dataclass, field
from datetime import datetime, timezone
from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class AccountDeleted(DomainEvent):
    user_id: str = ""
    event_type: str = "AccountDeleted"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
