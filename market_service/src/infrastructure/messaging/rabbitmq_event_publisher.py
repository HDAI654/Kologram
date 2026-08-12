"""RabbitMQ topic publisher for listing domain events."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any

from src.domain.events.base_event import DomainEvent
from src.domain.ports.event_publisher import EventPublisher
from src.exceptions import MessagingConnectionError, MessagingError

logger = logging.getLogger(__name__)


class RabbitMQEventPublisher(EventPublisher):
    """Publish domain events to a durable topic exchange after commit."""

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
        logger.info(
            "Connecting RabbitMQEventPublisher exchange=%s type=%s",
            self._exchange_name,
            self._exchange_type,
        )
        try:
            import aio_pika
            from aio_pika import ExchangeType
        except ImportError as exc:
            logger.exception("aio-pika is not installed")
            raise MessagingError("aio-pika is required for RabbitMQ publisher") from exc

        try:
            self._connection = await aio_pika.connect_robust(self._url)
            self._channel = await self._connection.channel()
            self._exchange = await self._channel.declare_exchange(
                self._exchange_name,
                ExchangeType(self._exchange_type),
                durable=True,
            )
        except Exception as exc:
            logger.exception(
                "Failed to connect RabbitMQEventPublisher exchange=%s",
                self._exchange_name,
            )
            raise MessagingConnectionError(
                f"Failed to connect to RabbitMQ: {exc}"
            ) from exc

        logger.info(
            "RabbitMQEventPublisher connected exchange=%s type=%s",
            self._exchange_name,
            self._exchange_type,
        )

    async def close(self) -> None:
        logger.info("Closing RabbitMQEventPublisher exchange=%s", self._exchange_name)
        try:
            if self._connection is not None and not self._connection.is_closed:
                await self._connection.close()
        except Exception:
            logger.exception("Error while closing RabbitMQ connection")
        finally:
            self._connection = None
            self._channel = None
            self._exchange = None
            logger.info(
                "RabbitMQEventPublisher closed exchange=%s", self._exchange_name
            )

    async def publish(self, event: DomainEvent) -> None:
        event_type = getattr(event, "event_type", None) or event.__class__.__name__
        if self._exchange is None:
            logger.error(
                "Publish rejected: publisher not connected event_type=%s", event_type
            )
            raise MessagingError("Publisher is not connected")

        import aio_pika

        payload = self._serialize(event)
        body = json.dumps(payload).encode("utf-8")
        routing_key = event_type

        logger.info(
            "Publishing event_type=%s routing_key=%s exchange=%s payload_keys=%s",
            event_type,
            routing_key,
            self._exchange_name,
            sorted(payload.keys()),
        )
        try:
            await self._exchange.publish(
                aio_pika.Message(
                    body=body,
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key,
            )
        except Exception as exc:
            logger.exception(
                "Failed to publish event_type=%s exchange=%s",
                event_type,
                self._exchange_name,
            )
            raise MessagingError(f"Failed to publish event: {exc}") from exc

        logger.info(
            "Published event_type=%s routing_key=%s exchange=%s",
            event_type,
            routing_key,
            self._exchange_name,
        )

    @staticmethod
    def _serialize(event: DomainEvent) -> dict[str, Any]:
        data = asdict(event)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data
