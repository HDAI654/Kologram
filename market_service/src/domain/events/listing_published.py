from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.events.base_event import DomainEvent


@dataclass(frozen=True, slots=True)
class ListingPublished(DomainEvent):
    listing_id: str = ""
    seller_id: str = ""
    category_id: str = ""
    title: str = ""
    event_type: str = "ListingPublished"
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
