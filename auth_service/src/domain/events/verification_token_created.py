from dataclasses import dataclass, field
from datetime import datetime, timezone
from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class VerificationTokenCreated(DomainEvent):
    token: str = ""
    email: str = ""
    token_type: str = ""
    event_type: str = "VerificationTokenCreated"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
