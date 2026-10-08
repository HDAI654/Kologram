"""Composition root: notification_dispatcher worker process."""

from __future__ import annotations

import logging
import signal
import sys

from src.application.factory import build_dispatcher, build_email_sender
from src.conf import Config
from src.infrastructure.messaging.rabbitmq_consumer import RabbitMQConsumer
from src.infrastructure.persistence.sqlite_idempotency import SqliteIdempotencyStore


def _configure_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def main() -> int:
    _configure_logging()
    log = logging.getLogger("worker")
    log.info(
        "starting %s env=%s email_enabled=%s",
        Config.APP_NAME,
        Config.APP_ENV,
        Config.EMAIL_ENABLED,
    )

    idempotency = SqliteIdempotencyStore(Config.IDEMPOTENCY_DB_PATH)
    email_sender = build_email_sender()
    dispatcher = build_dispatcher(email_sender, idempotency)

    def dispatch(idem_key: str, event_type: str, payload: dict) -> None:
        dispatcher.dispatch(
            idempotency_key=idem_key,
            event_type=event_type,
            payload=payload,
        )

    consumer = RabbitMQConsumer(
        url=Config.RABBITMQ_URL,
        queue=Config.RABBITMQ_QUEUE,
        exchanges=Config.exchanges(),
        prefetch=Config.RABBITMQ_PREFETCH,
        dispatch=dispatch,
    )

    def _shutdown(signum, frame) -> None:  # noqa: ARG001
        log.info("shutdown signal=%s", signum)
        consumer.close()
        idempotency.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    try:
        consumer.connect()
        consumer.start()
    except Exception:
        log.exception("worker failed")
        consumer.close()
        idempotency.close()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
