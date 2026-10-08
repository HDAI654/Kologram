"""Notification job contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NotificationJob(ABC):
    """One handler for a specific event type (or token_type subtype)."""

    event_type: str

    @abstractmethod
    def handle(self, payload: dict[str, Any]) -> None:
        """Process trusted payload. May send email or be a temporary no-op."""
