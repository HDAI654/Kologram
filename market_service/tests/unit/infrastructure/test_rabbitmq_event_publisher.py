import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from src.exceptions import MessagingConnectionError, MessagingError
from src.infrastructure.messaging.rabbitmq_event_publisher import (
    RabbitMQEventPublisher,
)

URL = "amqp://guest:guest@localhost:5672/"
EXCHANGE = "market.events"


@dataclass(frozen=True, slots=True)
class _SampleEvent:
    event_type: str = "ListingCreated"
    listing_id: str = ""
    seller_id: str = ""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class _AnonymousEvent:
    listing_id: str = ""


@pytest.fixture
def publisher() -> RabbitMQEventPublisher:
    return RabbitMQEventPublisher(
        url=URL, exchange_name=EXCHANGE, exchange_type="topic"
    )


class TestConnect:
    async def test_connect_declares_durable_topic_exchange(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()

        fake_aio_pika.connect_robust.assert_awaited_once_with(URL)
        fake_aio_pika.connection.channel.assert_awaited_once()
        fake_aio_pika.channel.declare_exchange.assert_awaited_once_with(
            EXCHANGE, "topic", durable=True
        )

    async def test_connect_sets_exchange_reference(self, publisher, fake_aio_pika):
        await publisher.connect()
        assert publisher._exchange is fake_aio_pika.exchange
        assert publisher._channel is fake_aio_pika.channel
        assert publisher._connection is fake_aio_pika.connection

    async def test_connect_wraps_driver_failure_in_messaging_connection_error(
        self, publisher, fake_aio_pika
    ):
        fake_aio_pika.connect_robust.side_effect = RuntimeError("boom")

        with pytest.raises(MessagingConnectionError):
            await publisher.connect()

    async def test_connect_preserves_cause(self, publisher, fake_aio_pika):
        underlying = RuntimeError("boom")
        fake_aio_pika.connect_robust.side_effect = underlying

        with pytest.raises(MessagingConnectionError) as exc_info:
            await publisher.connect()

        assert exc_info.value.__cause__ is underlying


class TestPublish:
    async def test_publish_before_connect_raises_messaging_error(self, publisher):
        with pytest.raises(MessagingError):
            await publisher.publish(_SampleEvent())

    async def test_publish_serializes_event_to_json(self, publisher, fake_aio_pika):
        await publisher.connect()
        event = _SampleEvent(listing_id="listing-1", seller_id="seller-1")

        await publisher.publish(event)

        assert len(fake_aio_pika.exchange.published) == 1
        message, routing_key = fake_aio_pika.exchange.published[0]
        assert routing_key == "ListingCreated"
        assert message.content_type == "application/json"
        assert message.delivery_mode == fake_aio_pika.DeliveryMode.PERSISTENT

        payload = json.loads(message.body.decode("utf-8"))
        assert payload["event_type"] == "ListingCreated"
        assert payload["listing_id"] == "listing-1"
        assert payload["seller_id"] == "seller-1"

    async def test_publish_converts_datetime_to_isoformat(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()
        moment = datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc)
        event = _SampleEvent(occurred_at=moment)

        await publisher.publish(event)

        message, _ = fake_aio_pika.exchange.published[0]
        payload = json.loads(message.body.decode("utf-8"))
        assert payload["occurred_at"] == moment.isoformat()

    async def test_publish_uses_class_name_when_event_type_missing(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()

        await publisher.publish(_AnonymousEvent())

        _, routing_key = fake_aio_pika.exchange.published[0]
        assert routing_key == "_AnonymousEvent"

    async def test_publish_wraps_exchange_failure_in_messaging_error(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()
        fake_aio_pika.exchange.publish.side_effect = RuntimeError("rejected")

        with pytest.raises(MessagingError):
            await publisher.publish(_SampleEvent())

    async def test_publish_error_preserves_cause(self, publisher, fake_aio_pika):
        await publisher.connect()
        underlying = RuntimeError("rejected")
        fake_aio_pika.exchange.publish.side_effect = underlying

        with pytest.raises(MessagingError) as exc_info:
            await publisher.publish(_SampleEvent())

        assert exc_info.value.__cause__ is underlying

    async def test_publish_does_not_reach_exchange_when_disconnected(
        self, publisher, fake_aio_pika
    ):
        with pytest.raises(MessagingError):
            await publisher.publish(_SampleEvent())

        fake_aio_pika.exchange.publish.assert_not_awaited()


class TestClose:
    async def test_close_closes_open_connection(self, publisher, fake_aio_pika):
        await publisher.connect()
        connection = fake_aio_pika.connection

        await publisher.close()

        connection.close.assert_awaited_once()
        assert publisher._connection is None
        assert publisher._channel is None
        assert publisher._exchange is None

    async def test_close_is_safe_when_never_connected(self, publisher):
        await publisher.close()
        assert publisher._connection is None

    async def test_close_skips_already_closed_connection(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()
        connection = fake_aio_pika.connection
        connection.is_closed = True

        await publisher.close()

        connection.close.assert_not_awaited()

    async def test_close_swallows_connection_close_error(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()
        fake_aio_pika.connection.close.side_effect = RuntimeError("already gone")

        await publisher.close()

        assert publisher._connection is None


class TestSerialize:
    def test_serialize_converts_dataclass_fields(self):
        event = _SampleEvent(listing_id="listing-1", seller_id="seller-1")

        result = RabbitMQEventPublisher._serialize(event)

        assert result["listing_id"] == "listing-1"
        assert result["seller_id"] == "seller-1"
        assert result["event_type"] == "ListingCreated"

    def test_serialize_converts_datetime_fields_to_isoformat(self):
        moment = datetime(2024, 1, 1, tzinfo=timezone.utc)
        event = _SampleEvent(occurred_at=moment)

        result = RabbitMQEventPublisher._serialize(event)

        assert result["occurred_at"] == "2024-01-01T00:00:00+00:00"
