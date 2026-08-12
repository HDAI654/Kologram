"""No-op event publisher."""

import logging

from src.domain.events.base_event import DomainEvent
from src.domain.ports.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class NoOpEventPublisher(EventPublisher):
    async def publish(self, event: DomainEvent) -> None:
        logger.debug("NoOpEventPublisher: drop event_type=%s", event.event_type)
