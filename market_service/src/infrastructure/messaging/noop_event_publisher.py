import logging

from src.domain.events.base_event import DomainEvent
from src.domain.ports.event_publisher import EventPublisher

logger = logging.getLogger(__name__)


class NoOpEventPublisher(EventPublisher):
    """Discard events — used when RABBITMQ_ENABLED=false."""

    async def publish(self, event: DomainEvent) -> None:
        logger.debug(
            "NoOp publish event_type=%s",
            getattr(event, "event_type", type(event).__name__),
        )
