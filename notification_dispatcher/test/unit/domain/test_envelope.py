"""Unit tests for event envelope parsing."""

from __future__ import annotations

import json

import pytest

from src.domain.events.envelope import parse_incoming_event, require_fields
from src.exceptions import InvalidEventError


def test_parse_valid_user_registered():
    body = json.dumps(
        {
            "user_id": "u1",
            "email": "a@b.com",
            "event_type": "UserRegistered",
            "occurred_at": "2026-08-13T10:00:00+00:00",
        }
    ).encode()
    event = parse_incoming_event(body)
    assert event.event_type == "UserRegistered"
    assert event.get("email") == "a@b.com"
    assert event.idempotency_key.startswith("UserRegistered:")


def test_parse_empty_body():
    with pytest.raises(InvalidEventError):
        parse_incoming_event(b"")


def test_parse_invalid_json():
    with pytest.raises(InvalidEventError):
        parse_incoming_event(b"{")


def test_parse_missing_event_type():
    with pytest.raises(InvalidEventError):
        parse_incoming_event(json.dumps({"user_id": "x"}).encode())


def test_require_fields():
    body = json.dumps({"event_type": "X", "user_id": "1"}).encode()
    event = parse_incoming_event(body)
    require_fields(event, "user_id")
    with pytest.raises(InvalidEventError):
        require_fields(event, "email")


def test_explicit_event_id_in_key():
    body = json.dumps(
        {"event_type": "UserRegistered", "event_id": "abc-123", "email": "a@b.com"}
    ).encode()
    event = parse_incoming_event(body)
    assert event.idempotency_key == "UserRegistered:abc-123"
