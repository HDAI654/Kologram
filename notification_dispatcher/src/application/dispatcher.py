"""Route trusted event payloads to notification jobs."""

from __future__ import annotations

import logging
from typing import Any

from src.application.jobs.base import NotificationJob
from src.domain.ports.idempotency_store import IdempotencyStore
from src.exceptions import UnknownEventTypeError

logger = logging.getLogger(__name__)


class Dispatcher:
    def __init__(
        self,
        jobs: dict[str, NotificationJob],
        idempotency: IdempotencyStore,
        *,
        verification_jobs: dict[str, NotificationJob] | None = None,
    ) -> None:
        """
        jobs: event_type → job (except VerificationTokenCreated routed via verification_jobs).
        verification_jobs: token_type → job for VerificationTokenCreated.
        """
        self._jobs = jobs
        self._verification_jobs = verification_jobs or {}
        self._idempotency = idempotency

    def dispatch(self, *, idempotency_key: str, event_type: str, payload: dict[str, Any]) -> None:
        if self._idempotency.already_processed(idempotency_key):
            logger.info("skip already processed key=%s event_type=%s", idempotency_key, event_type)
            return

        if event_type == "VerificationTokenCreated":
            token_type = str(payload.get("token_type", "")).strip()
            job = self._verification_jobs.get(token_type)
            if job is None:
                logger.warning(
                    "VerificationTokenCreated unknown token_type=%s; skip",
                    token_type,
                )
                self._idempotency.mark_processed(idempotency_key)
                return
            job.handle(payload)
            self._idempotency.mark_processed(idempotency_key)
            return

        job = self._jobs.get(event_type)
        if job is None:
            raise UnknownEventTypeError(f"no handler for event_type={event_type}")

        job.handle(payload)
        self._idempotency.mark_processed(idempotency_key)
