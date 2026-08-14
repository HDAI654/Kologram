"""E2E-style journey without real RabbitMQ: body → dispatcher → email sink."""

from __future__ import annotations

import json

import pytest

from src.application.dispatcher import EventDispatcher
from src.infrastructure.email.console_sender import ConsoleEmailSender
from src.infrastructure.persistence.idempotency import InMemoryIdempotencyStore


def event(et: str, **kw) -> bytes:
    payload = {"event_type": et, "occurred_at": "2026-08-13T12:00:00+00:00", **kw}
    return json.dumps(payload).encode()


@pytest.mark.asyncio
async def test_full_auth_market_mix():
    sender = ConsoleEmailSender()
    dispatcher = EventDispatcher(sender, InMemoryIdempotencyStore())

    events = [
        event("UserRegistered", user_id="u1", email="u@example.com"),
        event(
            "VerificationTokenCreated",
            email="u@example.com",
            token="tok-1",
            token_type="email_verify",
        ),
        event(
            "UserLoggedIn",
            user_id="u1",
            email="u@example.com",
            session_id="s1",
            device="iOS",
        ),
        event("CategoryCreated", category_id="c1", name="Home"),
        event(
            "ListingCreated",
            listing_id="l1",
            seller_id="u1",
            title="Lamp",
            status="DRAFT",
            email="u@example.com",
            category_id="c1",
        ),
        event(
            "ListingPublished",
            listing_id="l1",
            seller_id="u1",
            title="Lamp",
            category_id="c1",
            email="u@example.com",
        ),
    ]
    for body in events:
        result = await dispatcher.process_body(body)
        assert result.status == "processed"

    templates = [m.template_key for m in sender.sent]
    assert templates == [
        "user_registered",
        "verification_token_created",
        "user_logged_in",
        "category_created",
        "listing_created",
        "listing_published",
    ]
    # Token only in verification email context
    assert sender.sent[1].context["token"] == "tok-1"
    assert "token" not in sender.sent[0].context
