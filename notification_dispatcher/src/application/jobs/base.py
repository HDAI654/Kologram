"""Notification job protocol and shared helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from src.domain.events.envelope import IncomingEvent
from src.domain.notifications.email_message import EmailMessage, NotificationSpec
from src.exceptions import MissingRecipientError


class NotificationJob(ABC):
    """Builds an EmailMessage from an IncomingEvent (no delivery)."""

    event_type: str

    @abstractmethod
    def build(self, event: IncomingEvent) -> EmailMessage:
        raise NotImplementedError

    @abstractmethod
    def spec(self) -> NotificationSpec:
        raise NotImplementedError


def resolve_recipient(
    event: IncomingEvent,
    *,
    preferred_keys: tuple[str, ...] = ("email", "recipient_email"),
    admin_email: str | None = None,
    allow_admin_fallback: bool = False,
) -> str:
    """Resolve recipient email from event payload.

    Prefer explicit email fields on the event. Optional admin fallback for
    operational notifications (e.g. CategoryCreated).
    """
    for key in preferred_keys:
        value = event.payload.get(key)
        if isinstance(value, str) and "@" in value.strip():
            return value.strip().lower()
    if allow_admin_fallback and admin_email and "@" in admin_email:
        return admin_email.strip().lower()
    raise MissingRecipientError(
        f"No recipient email on event {event.event_type}; "
        f"looked for keys {preferred_keys}"
    )


def base_context(event: IncomingEvent, **extra: Any) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "event_type": event.event_type,
        "occurred_at": event.occurred_at,
    }
    ctx.update(extra)
    return ctx
