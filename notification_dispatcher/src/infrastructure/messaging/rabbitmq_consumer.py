"""Blocking RabbitMQ consumer for domain event exchanges."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

import pika

from src.exceptions import MessagingError

logger = logging.getLogger(__name__)

DispatchFn = Callable[[str, str, dict[str, Any]], None]
# (idempotency_key, event_type, payload)


class RabbitMQConsumer:
    def __init__(
        self,
        *,
        url: str,
        queue: str,
        exchanges: list[str],
        prefetch: int,
        dispatch: DispatchFn,
    ) -> None:
        self._url = url
        self._queue = queue
        self._exchanges = exchanges
        self._prefetch = prefetch
        self._dispatch = dispatch
        self._connection: pika.BlockingConnection | None = None
        self._channel = None

    def connect(self) -> None:
        try:
            params = pika.URLParameters(self._url)
            self._connection = pika.BlockingConnection(params)
            self._channel = self._connection.channel()
            self._channel.basic_qos(prefetch_count=self._prefetch)
            self._channel.queue_declare(queue=self._queue, durable=True)
            for exchange in self._exchanges:
                self._channel.exchange_declare(
                    exchange=exchange,
                    exchange_type="topic",
                    durable=True,
                )
                self._channel.queue_bind(
                    queue=self._queue,
                    exchange=exchange,
                    routing_key="#",
                )
            logger.info(
                "consumer ready queue=%s exchanges=%s",
                self._queue,
                self._exchanges,
            )
        except Exception as exc:
            raise MessagingError(f"failed to connect consumer: {exc}") from exc

    def start(self) -> None:
        if self._channel is None:
            self.connect()
        assert self._channel is not None

        def on_message(ch, method, properties, body: bytes) -> None:
            try:
                payload = json.loads(body.decode("utf-8"))
                if not isinstance(payload, dict):
                    logger.error("invalid payload type; ack and skip")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                event_type = (
                    str(payload.get("event_type") or "")
                    or str(getattr(method, "routing_key", "") or "")
                )
                if not event_type:
                    logger.error("missing event_type; ack and skip")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                message_id = None
                if properties is not None:
                    message_id = properties.message_id
                idem_key = str(message_id or f"{method.exchange}:{method.routing_key}:{body!r}")

                self._dispatch(idem_key, event_type, payload)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception:
                logger.exception("handler failed; ack to avoid poison loop")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        self._channel.basic_consume(queue=self._queue, on_message_callback=on_message)
        logger.info("start consuming queue=%s", self._queue)
        self._channel.start_consuming()

    def close(self) -> None:
        try:
            if self._channel is not None and self._channel.is_open:
                self._channel.close()
            if self._connection is not None and self._connection.is_open:
                self._connection.close()
        except Exception:
            logger.exception("error closing consumer")
