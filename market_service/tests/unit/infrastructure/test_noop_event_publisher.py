import logging

import pytest

from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher


class _EventWithType:
    event_type = "ListingCreated"


class _EventWithoutType:
    pass


class TestNoOpEventPublisher:
    async def test_publish_accepts_event_with_event_type(self):
        publisher = NoOpEventPublisher()
        await publisher.publish(_EventWithType())

    async def test_publish_accepts_event_without_event_type(self):
        publisher = NoOpEventPublisher()
        await publisher.publish(_EventWithoutType())

    async def test_publish_logs_event_type_attribute(
        self, caplog: pytest.LogCaptureFixture
    ):
        publisher = NoOpEventPublisher()
        with caplog.at_level(logging.DEBUG):
            await publisher.publish(_EventWithType())

        assert any("ListingCreated" in r.getMessage() for r in caplog.records)

    async def test_publish_logs_class_name_when_event_type_missing(
        self, caplog: pytest.LogCaptureFixture
    ):
        publisher = NoOpEventPublisher()
        with caplog.at_level(logging.DEBUG):
            await publisher.publish(_EventWithoutType())

        assert any("_EventWithoutType" in r.getMessage() for r in caplog.records)

    async def test_multiple_publishes_do_not_raise(self):
        publisher = NoOpEventPublisher()
        for _ in range(3):
            await publisher.publish(_EventWithType())

    async def test_publisher_is_subclass_of_event_publisher_port(self):
        from src.domain.ports.event_publisher import EventPublisher

        assert issubclass(NoOpEventPublisher, EventPublisher)
