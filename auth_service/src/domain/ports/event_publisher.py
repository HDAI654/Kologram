from abc import ABC, abstractmethod
from src.domain.events.base_event import DomainEvent


class EventPublisher(ABC):
    """Publishes integration events after successful use-case commits."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError
