"""Test / local email sink — captures messages without network I/O."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from src.domain.notifications.email_message import EmailMessage
from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger(__name__)


@dataclass
class ConsoleEmailSender(EmailSender):
    """In-memory capture for tests and development."""

    sent: list[EmailMessage] = field(default_factory=list)
    fail_next: bool = False

    async def send(self, message: EmailMessage) -> None:
        if self.fail_next:
            self.fail_next = False
            from src.exceptions import EmailDeliveryError

            raise EmailDeliveryError("Simulated delivery failure")
        self.sent.append(message)
        # Log only non-secret metadata.
        logger.info(
            "Email captured template=%s to_hash=%s keys=%s",
            message.template_key,
            hash(message.to) % 10_000,
            sorted(k for k in message.context if k != "token"),
        )
