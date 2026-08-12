from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class CategoryCreated(DomainEvent):
    category_id: str = ""
    name: str = ""
    parent_id: str | None = None
    event_type: str = "CategoryCreated"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
