from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class ListingCreated(DomainEvent):
    listing_id: str = ""
    seller_id: str = ""
    category_id: str = ""
    title: str = ""
    status: str = ""
    event_type: str = "ListingCreated"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
