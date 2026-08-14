"""Event → notification job dispatcher."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from src.application.jobs.auth_jobs import (
    AccountDeletedJob,
    UserLoggedInJob,
    UserLoggedOutJob,
    UserRegisteredJob,
    VerificationTokenCreatedJob,
)
from src.application.jobs.base import NotificationJob
from src.application.jobs.market_jobs import (
    CategoryCreatedJob,
    ListingCreatedJob,
    ListingDeletedJob,
    ListingPublishedJob,
    ListingStatusChangedJob,
    ListingUpdatedJob,
)
from src.domain.events.envelope import IncomingEvent, parse_incoming_event
from src.domain.ports.email_sender import EmailSender
from src.domain.ports.idempotency_store import IdempotencyStore
from src.exceptions import (
    EmailDeliveryError,
    PermanentProcessingError,
    TransientProcessingError,
    UnknownEventTypeError,
)

logger = logging.getLogger(__name__)


def default_job_registry() -> dict[str, NotificationJob]:
    jobs: list[NotificationJob] = [
        AccountDeletedJob(),
        UserLoggedInJob(),
        UserLoggedOutJob(),
        UserRegisteredJob(),
        VerificationTokenCreatedJob(),
        CategoryCreatedJob(),
        ListingCreatedJob(),
        ListingDeletedJob(),
        ListingPublishedJob(),
        ListingStatusChangedJob(),
        ListingUpdatedJob(),
    ]
    return {j.event_type: j for j in jobs}


@dataclass(slots=True)
class ProcessResult:
    event_type: str
    idempotency_key: str
    status: str  # processed|duplicate|unknown|failed
    duration_ms: float


class EventDispatcher:
    """Parse → classify → job → email → idempotency mark."""

    def __init__(
        self,
        email_sender: EmailSender,
        idempotency_store: IdempotencyStore | None = None,
        jobs: dict[str, NotificationJob] | None = None,
    ) -> None:
        self._email = email_sender
        self._idem = idempotency_store
        self._jobs = jobs or default_job_registry()

    async def process_body(self, body: bytes) -> ProcessResult:
        started = time.perf_counter()
        event = parse_incoming_event(body)
        return await self.process_event(event, started=started)

    async def process_event(
        self,
        event: IncomingEvent,
        *,
        started: float | None = None,
    ) -> ProcessResult:
        t0 = started if started is not None else time.perf_counter()
        event_type = event.event_type
        key = event.idempotency_key

        logger.info(
            "Processing event_type=%s idempotency_key=%s",
            event_type,
            key[:16] + "…",
        )

        if self._idem is not None and await self._idem.already_processed(key):
            logger.info("Duplicate event skipped event_type=%s", event_type)
            return ProcessResult(
                event_type=event_type,
                idempotency_key=key,
                status="duplicate",
                duration_ms=(time.perf_counter() - t0) * 1000,
            )

        job = self._jobs.get(event_type)
        if job is None:
            logger.warning("Unknown event_type=%s — permanent reject", event_type)
            raise UnknownEventTypeError(f"Unsupported event_type={event_type}")

        message = job.build(event)

        # Never log verification tokens or full security payloads.
        safe_ctx_keys = sorted(k for k in message.context if k != "token")
        logger.info(
            "Dispatching template=%s to_domain=%s context_keys=%s security=%s",
            message.template_key,
            message.to.split("@")[-1] if "@" in message.to else "invalid",
            safe_ctx_keys,
            message.is_security_sensitive,
        )

        try:
            await self._email.send(message)
        except EmailDeliveryError:
            raise TransientProcessingError("Email delivery failed") from None
        except Exception as exc:
            logger.exception("Unexpected email failure event_type=%s", event_type)
            raise TransientProcessingError(str(exc)) from exc

        if self._idem is not None:
            await self._idem.mark_processed(key, event_type)

        duration_ms = (time.perf_counter() - t0) * 1000
        logger.info(
            "Processed event_type=%s status=processed duration_ms=%.1f",
            event_type,
            duration_ms,
        )
        return ProcessResult(
            event_type=event_type,
            idempotency_key=key,
            status="processed",
            duration_ms=duration_ms,
        )


def classify_error(exc: BaseException) -> str:
    """Return 'permanent' or 'transient' for ACK strategy."""
    if isinstance(exc, PermanentProcessingError):
        return "permanent"
    if isinstance(exc, TransientProcessingError):
        return "transient"
    return "transient"
