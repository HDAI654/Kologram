"""RabbitMQ consumer: bind topic exchanges → queue, manual ACK/NACK."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from src.application.dispatcher import EventDispatcher, classify_error
from src.conf import Config
from src.exceptions import PermanentProcessingError, TransientProcessingError

logger = logging.getLogger(__name__)

ProcessFn = Callable[[bytes], Awaitable[object]]


class RabbitMQConsumer:
    """aio-pika based consumer with DLX and manual acknowledgements."""

    def __init__(
        self,
        dispatcher: EventDispatcher,
        *,
        url: str | None = None,
        queue_name: str | None = None,
        exchanges: list[str] | None = None,
        routing_keys: list[str] | None = None,
        prefetch: int | None = None,
        dlx: str | None = None,
        dlq: str | None = None,
    ) -> None:
        self._dispatcher = dispatcher
        self._url = url or Config.RABBITMQ_URL
        self._queue_name = queue_name or Config.RABBITMQ_QUEUE
        self._exchanges = exchanges or Config.exchanges()
        self._routing_keys = routing_keys or Config.routing_keys()
        self._prefetch = prefetch if prefetch is not None else Config.RABBITMQ_PREFETCH
        self._dlx = dlx or Config.RABBITMQ_DLX
        self._dlq = dlq or Config.RABBITMQ_DLQ
        self._connection = None
        self._channel = None
        self._queue = None
        self._consumer_tag = None
        self._stopping = asyncio.Event()

    async def connect(self) -> None:
        import aio_pika
        from aio_pika import ExchangeType

        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=self._prefetch)

        # Dead-letter exchange + queue
        dlx = await self._channel.declare_exchange(
            self._dlx, ExchangeType.FANOUT, durable=True
        )
        dlq = await self._channel.declare_queue(self._dlq, durable=True)
        await dlq.bind(dlx)

        self._queue = await self._channel.declare_queue(
            self._queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self._dlx,
            },
        )

        for name in self._exchanges:
            exchange = await self._channel.declare_exchange(
                name, ExchangeType.TOPIC, durable=True
            )
            keys = self._routing_keys or ["#"]
            for rk in keys:
                await self._queue.bind(exchange, routing_key=rk)
                logger.info(
                    "Bound queue=%s exchange=%s routing_key=%s",
                    self._queue_name,
                    name,
                    rk,
                )

        logger.info("RabbitMQConsumer ready queue=%s", self._queue_name)

    async def start_consuming(self) -> None:
        assert self._queue is not None
        self._stopping.clear()
        self._consumer_tag = await self._queue.consume(self._on_message, no_ack=False)
        logger.info("Consumer started tag=%s", self._consumer_tag)
        await self._stopping.wait()

    async def stop(self) -> None:
        self._stopping.set()
        if self._queue is not None and self._consumer_tag is not None:
            try:
                await self._queue.cancel(self._consumer_tag)
            except Exception:
                logger.exception("Failed to cancel consumer")
            self._consumer_tag = None

    async def close(self) -> None:
        await self.stop()
        if self._connection is not None and not self._connection.is_closed:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._queue = None

    async def _on_message(self, message) -> None:
        body = message.body
        try:
            await self._dispatcher.process_body(body)
            await message.ack()
        except PermanentProcessingError as exc:
            logger.warning(
                "Permanent failure — reject to DLQ: %s",
                exc,
            )
            # requeue=False → DLX when configured
            await message.reject(requeue=False)
        except TransientProcessingError as exc:
            logger.warning("Transient failure — nack requeue: %s", exc)
            await message.nack(requeue=True)
        except Exception:
            logger.exception("Unhandled consumer error — nack requeue")
            await message.nack(requeue=True)
