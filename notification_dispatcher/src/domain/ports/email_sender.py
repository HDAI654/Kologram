from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.notifications.email_message import EmailMessage


class EmailSender(ABC):
    """Port for delivering an EmailMessage."""

    @abstractmethod
    async def send(self, message: EmailMessage) -> None:
        raise NotImplementedError
