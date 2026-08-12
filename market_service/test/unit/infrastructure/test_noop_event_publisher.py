import pytest

from src.domain.events.listing_created import ListingCreated
from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher


@pytest.mark.asyncio
async def test_noop_publish() -> None:
    pub = NoOpEventPublisher()
    await pub.publish(
        ListingCreated(
            listing_id="550e8400-e29b-41d4-a716-446655440001",
            seller_id="550e8400-e29b-41d4-a716-446655440002",
            category_id="550e8400-e29b-41d4-a716-446655440003",
            title="x",
            status="DRAFT",
        )
    )
