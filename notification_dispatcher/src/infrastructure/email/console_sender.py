"""Log email to the process logger instead of sending."""

from __future__ import annotations

import logging

from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger(__name__)


class ConsoleEmailSender(EmailSender):
    def send(self, *, to: str, subject: str, body: str) -> None:
        logger.info(
            "console email\nto=%s\nsubject=%s\n---\n%s\n---",
            to,
            subject,
            body,
        )
