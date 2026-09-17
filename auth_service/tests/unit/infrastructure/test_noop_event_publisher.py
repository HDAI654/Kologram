import logging

import pytest

from src.infrastructure.messaging.noop_event_publisher import NoOpEventPublisher


class _FakeEvent:
    event_type = "TestEvent"


class TestNoOpEventPublisher:
    async def test_publish_does_not_raise(self):
        publisher = NoOpEventPublisher()
        await publisher.publish(_FakeEvent())

    async def test_publish_logs_event_type(self, caplog):
        publisher = NoOpEventPublisher()
        with caplog.at_level(logging.DEBUG):
            await publisher.publish(_FakeEvent())
        assert any("TestEvent" in record.getMessage() for record in caplog.records)

    async def test_multiple_publishes_ok(self):
        publisher = NoOpEventPublisher()
        for _ in range(3):
            await publisher.publish(_FakeEvent())