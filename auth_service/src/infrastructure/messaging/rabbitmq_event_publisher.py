"""RabbitMQ topic publisher for auth domain events."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any

from src.domain.events.base_event import DomainEvent
from src.domain.ports.event_publisher import EventPublisher
from src.exceptions import MessagingError

logger = logging.getLogger(__name__)


class RabbitMQEventPublisher(EventPublisher):
    def __init__(
        self,
        url: str,
        exchange_name: str,
        exchange_type: str = "topic",
    ) -> None:
        self._url = url
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._connection = None
        self._channel = None
        self._exchange = None

    async def connect(self) -> None:
        try:
            import aio_pika
            from aio_pika import ExchangeType
        except ImportError as exc:
            raise MessagingError("aio-pika is required") from exc

        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.declare_exchange(
            self._exchange_name,
            ExchangeType(self._exchange_type),
            durable=True,
        )
        logger.info("RabbitMQEventPublisher connected exchange=%s", self._exchange_name)

    async def close(self) -> None:
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None

    async def publish(self, event: DomainEvent) -> None:
        if self._exchange is None:
            raise MessagingError("Publisher is not connected")
        import aio_pika

        payload = self._serialize(event)
        body = json.dumps(payload).encode("utf-8")
        await self._exchange.publish(
            aio_pika.Message(body=body, content_type="application/json"),
            routing_key=event.event_type or event.__class__.__name__,
        )
        logger.debug("Published event_type=%s", event.event_type)

    @staticmethod
    def _serialize(event: DomainEvent) -> dict[str, Any]:
        data = asdict(event)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
