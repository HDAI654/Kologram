"""Email message value object and notification specification.

Templates / prose are owned by a later task. Jobs build EmailMessage with
structured data only (no full body copy).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EmailMessage:
    """Outbound email envelope prepared by a notification job.

    ``template_key`` selects the template; ``context`` supplies dynamic fields.
    The email adapter is responsible for rendering (or, for tests, capturing).
    """

    to: str
    subject_key: str
    template_key: str
    context: dict[str, Any] = field(default_factory=dict)
    from_address: str | None = None
    is_security_sensitive: bool = False


@dataclass(frozen=True, slots=True)
class NotificationSpec:
    """Human-readable requirements for a notification (no email prose).

    Used by tests and documentation; jobs embed the same field requirements
    into EmailMessage.context.
    """

    event_type: str
    purpose: str
    recipient_source: str
    subject_intent: str
    required_context_keys: tuple[str, ...]
    optional_context_keys: tuple[str, ...] = ()
    security_notes: str = ""
    is_security_sensitive: bool = False
