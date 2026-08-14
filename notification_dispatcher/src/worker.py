"""Entrypoint: notification-dispatcher consumer worker."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys

from src.application.dispatcher import EventDispatcher
from src.conf import Config
from src.infrastructure.email.console_sender import ConsoleEmailSender
from src.infrastructure.email.smtp_sender import SMTPEmailSender
from src.infrastructure.persistence.idempotency import (
    InMemoryIdempotencyStore,
    SQLiteIdempotencyStore,
)
from src.infrastructure.rabbitmq.consumer import RabbitMQConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


def build_email_sender():
    if Config.EMAIL_PROVIDER == "smtp" and Config.EMAIL_ENABLED:
        return SMTPEmailSender()
    return ConsoleEmailSender()


async def build_idempotency_store():
    if not Config.IDEMPOTENCY_ENABLED:
        return None
    url = Config.IDEMPOTENCY_DB_URL
    if url in (":memory:", "sqlite+aiosqlite:///:memory:"):
        return InMemoryIdempotencyStore()
    store = SQLiteIdempotencyStore(url)
    # Ensure parent dir exists for file-backed SQLite.
    if "://" in url:
        path = url.split(":///", 1)[-1]
    else:
        path = url
    if path != ":memory:":
        from pathlib import Path

        Path(path).parent.mkdir(parents=True, exist_ok=True)
    await store.connect()
    return store


async def main() -> int:
    logger.info(
        "Starting %s env=%s exchanges=%s queue=%s",
        Config.APP_NAME,
        Config.APP_ENV,
        Config.exchanges(),
        Config.RABBITMQ_QUEUE,
    )
    email = build_email_sender()
    idem = await build_idempotency_store()
    dispatcher = EventDispatcher(email_sender=email, idempotency_store=idem)
    consumer = RabbitMQConsumer(dispatcher)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _signal_handler)
        except NotImplementedError:
            signal.signal(sig, lambda *_: _signal_handler())

    try:
        await consumer.connect()
        consume_task = asyncio.create_task(consumer.start_consuming())
        await stop_event.wait()
        await consumer.stop()
        consume_task.cancel()
        try:
            await consume_task
        except asyncio.CancelledError:
            pass
    finally:
        await consumer.close()
        if hasattr(idem, "close") and idem is not None:
            await idem.close()  # type: ignore[union-attr]
        logger.info("Worker stopped")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        sys.exit(0)
