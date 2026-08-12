from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class ListingStatusChanged(DomainEvent):
    listing_id: str = ""
    seller_id: str = ""
    old_status: str = ""
    new_status: str = ""
    event_type: str = "ListingStatusChanged"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
