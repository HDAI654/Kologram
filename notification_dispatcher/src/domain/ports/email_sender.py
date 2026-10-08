"""Port: deliver a plain-text email."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSender(ABC):
    @abstractmethod
    def send(self, *, to: str, subject: str, body: str) -> None:
        """Send plain-text email. Raises EmailSendError on failure."""
