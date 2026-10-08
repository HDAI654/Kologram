"""Chat event jobs — temporary NOTHING."""

from __future__ import annotations

import logging
from typing import Any

from src.application.jobs.base import NotificationJob

logger = logging.getLogger(__name__)


class ConversationStartedJob(NotificationJob):
    event_type = "ConversationStarted"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: inquiry emails deferred.
        logger.info(
            "ConversationStarted temporary NOTHING payload_keys=%s", list(payload.keys())
        )


class MessageSentJob(NotificationJob):
    event_type = "MessageSent"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: offline message email deferred (realtime is chat hub).
        logger.info("MessageSent temporary NOTHING payload_keys=%s", list(payload.keys()))
