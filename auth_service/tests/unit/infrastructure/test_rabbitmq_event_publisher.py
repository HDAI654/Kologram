import json
from dataclasses import dataclass, field
from datetime import datetime, timezone

import pytest

from src.exceptions import MessagingError
from src.infrastructure.messaging.rabbitmq_event_publisher import (
    RabbitMQEventPublisher,
)

URL = "amqp://guest:guest@localhost:5672/"
EXCHANGE = "auth.events"


@dataclass(frozen=True, slots=True)
class _SampleEvent:
    event_type: str = "UserRegistered"
    user_id: str = ""
    email: str = ""
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, slots=True)
class _AnonymousEvent:
    user_id: str = ""


@pytest.fixture
def publisher() -> RabbitMQEventPublisher:
    return RabbitMQEventPublisher(url=URL, exchange_name=EXCHANGE)


class TestConnect:
    async def test_declares_durable_topic_exchange(self, publisher, fake_aio_pika):
        await publisher.connect()

        fake_aio_pika.connect_robust.assert_awaited_once_with(URL)
        fake_aio_pika.connection.channel.assert_awaited_once()
        fake_aio_pika.channel.declare_exchange.assert_awaited_once()
        args = fake_aio_pika.channel.declare_exchange.call_args
        assert args.args[0] == EXCHANGE
        assert args.kwargs == {"durable": True}

    async def test_sets_internal_exchange_reference(self, publisher, fake_aio_pika):
        await publisher.connect()
        assert publisher._exchange is fake_aio_pika.exchange
        assert publisher._connection is fake_aio_pika.connection


class TestPublish:
    async def test_publish_before_connect_raises(self, publisher):
        with pytest.raises(MessagingError):
            await publisher.publish(_SampleEvent())

    async def test_publishes_serialized_payload(self, publisher, fake_aio_pika):
        await publisher.connect()
        event = _SampleEvent(user_id="u-1", email="user@example.com")

        await publisher.publish(event)

        assert len(fake_aio_pika.exchange.published) == 1
        message, routing_key = fake_aio_pika.exchange.published[0]
        assert routing_key == "UserRegistered"
        assert message.content_type == "application/json"
        payload = json.loads(message.body.decode("utf-8"))
        assert payload["user_id"] == "u-1"
        assert payload["email"] == "user@example.com"

    async def test_datetime_serialized_to_isoformat(self, publisher, fake_aio_pika):
        await publisher.connect()
        moment = datetime(2024, 5, 1, 12, 0, tzinfo=timezone.utc)

        await publisher.publish(_SampleEvent(occurred_at=moment))

        message, _ = fake_aio_pika.exchange.published[0]
        payload = json.loads(message.body.decode("utf-8"))
        assert payload["occurred_at"] == moment.isoformat()


class TestClose:
    async def test_close_closes_connection(self, publisher, fake_aio_pika):
        await publisher.connect()
        await publisher.close()
        fake_aio_pika.connection.close.assert_awaited_once()
        assert publisher._connection is None

    async def test_close_when_not_connected_is_safe(self, publisher):
        await publisher.close()
        assert publisher._connection is None

    async def test_close_skips_already_closed_connection(
        self, publisher, fake_aio_pika
    ):
        await publisher.connect()
        fake_aio_pika.connection.is_closed = True
        await publisher.close()
        fake_aio_pika.connection.close.assert_not_awaited()


class TestSerialize:
    def test_serialize_converts_dataclass(self):
        event = _SampleEvent(user_id="u-1", email="a@b.c")
        result = RabbitMQEventPublisher._serialize(event)
        assert result["user_id"] == "u-1"
        assert result["email"] == "a@b.c"

    def test_serialize_converts_datetime(self):
        moment = datetime(2024, 1, 1, tzinfo=timezone.utc)
        result = RabbitMQEventPublisher._serialize(_SampleEvent(occurred_at=moment))
        assert result["occurred_at"] == "2024-01-01T00:00:00+00:00"
