"""Parsed integration event envelope matching producer wire format."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.exceptions import InvalidEventError

SUPPORTED_EVENT_TYPES: frozenset[str] = frozenset(
    {
        "AccountDeleted",
        "UserLoggedIn",
        "UserLoggedOut",
        "UserRegistered",
        "VerificationTokenCreated",
        "CategoryCreated",
        "ListingCreated",
        "ListingDeleted",
        "ListingPublished",
        "ListingStatusChanged",
        "ListingUpdated",
    }
)


@dataclass(frozen=True, slots=True)
class IncomingEvent:
    """Normalized event after JSON parse + light validation."""

    event_type: str
    occurred_at: str | None
    payload: dict[str, Any]
    # Deterministic key for idempotency (producers currently omit event_id).
    idempotency_key: str
    raw_body: bytes

    def get(self, key: str, default: Any = None) -> Any:
        return self.payload.get(key, default)


def parse_incoming_event(body: bytes) -> IncomingEvent:
    """Parse producer JSON body into IncomingEvent.

    Raises InvalidEventError for permanent parse/structure failures.
    """
    if not body:
        raise InvalidEventError("Empty message body")
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidEventError(f"Invalid JSON body: {exc}") from exc

    if not isinstance(data, dict):
        raise InvalidEventError("Event body must be a JSON object")

    event_type = data.get("event_type")
    if not event_type or not isinstance(event_type, str):
        raise InvalidEventError("Missing or invalid event_type")

    occurred_at = data.get("occurred_at")
    if occurred_at is not None and not isinstance(occurred_at, str):
        occurred_at = str(occurred_at)

    # Stable idempotency key: prefer explicit event_id; else hash of body.
    event_id = data.get("event_id")
    if isinstance(event_id, str) and event_id.strip():
        key = f"{event_type}:{event_id.strip()}"
    else:
        digest = hashlib.sha256(body).hexdigest()
        key = f"{event_type}:{digest}"

    return IncomingEvent(
        event_type=event_type.strip(),
        occurred_at=occurred_at,
        payload=data,
        idempotency_key=key,
        raw_body=body,
    )


def require_fields(event: IncomingEvent, *fields: str) -> None:
    """Raise InvalidEventError if any required field is missing or empty."""
    missing = []
    for name in fields:
        value = event.payload.get(name)
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(name)
    if missing:
        raise InvalidEventError(
            f"Event {event.event_type} missing required fields: {', '.join(missing)}"
        )


def parse_occurred_at(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
