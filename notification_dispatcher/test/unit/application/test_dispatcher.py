"""Dispatcher and job unit tests (no RabbitMQ / SMTP)."""

from __future__ import annotations

import json

import pytest

from src.application.dispatcher import EventDispatcher, classify_error, default_job_registry
from src.exceptions import (
    PermanentProcessingError,
    TransientProcessingError,
    UnknownEventTypeError,
)
from src.infrastructure.email.console_sender import ConsoleEmailSender
from src.infrastructure.persistence.idempotency import InMemoryIdempotencyStore


@pytest.fixture
def sender() -> ConsoleEmailSender:
    return ConsoleEmailSender()


@pytest.fixture
def dispatcher(sender: ConsoleEmailSender) -> EventDispatcher:
    return EventDispatcher(
        email_sender=sender,
        idempotency_store=InMemoryIdempotencyStore(),
    )


def _body(event_type: str, **fields) -> bytes:
    payload = {"event_type": event_type, "occurred_at": "2026-08-13T12:00:00+00:00"}
    payload.update(fields)
    return json.dumps(payload).encode()


@pytest.mark.asyncio
async def test_user_registered(dispatcher: EventDispatcher, sender: ConsoleEmailSender):
    result = await dispatcher.process_body(
        _body("UserRegistered", user_id="u1", email="user@example.com")
    )
    assert result.status == "processed"
    assert len(sender.sent) == 1
    assert sender.sent[0].template_key == "user_registered"
    assert sender.sent[0].to == "user@example.com"


@pytest.mark.asyncio
async def test_user_logged_in_security_context(
    dispatcher: EventDispatcher, sender: ConsoleEmailSender
):
    await dispatcher.process_body(
        _body(
            "UserLoggedIn",
            user_id="u1",
            email="user@example.com",
            session_id="sess-1",
            device="Chrome/Linux",
            role="user",
        )
    )
    msg = sender.sent[0]
    assert msg.is_security_sensitive
    assert "guidance" in msg.context
    assert msg.context["session_id"] == "sess-1"


@pytest.mark.asyncio
async def test_verification_token_in_context_not_duplicated_on_replay(
    dispatcher: EventDispatcher, sender: ConsoleEmailSender
):
    body = _body(
        "VerificationTokenCreated",
        email="user@example.com",
        token="SECRET-TOKEN-XYZ",
        token_type="email_verify",
    )
    r1 = await dispatcher.process_body(body)
    r2 = await dispatcher.process_body(body)
    assert r1.status == "processed"
    assert r2.status == "duplicate"
    assert len(sender.sent) == 1
    assert sender.sent[0].context["token"] == "SECRET-TOKEN-XYZ"


@pytest.mark.asyncio
async def test_unknown_event(dispatcher: EventDispatcher):
    with pytest.raises(UnknownEventTypeError):
        await dispatcher.process_body(_body("SomethingElse", user_id="x"))


@pytest.mark.asyncio
async def test_missing_required_field(dispatcher: EventDispatcher):
    with pytest.raises(PermanentProcessingError):
        await dispatcher.process_body(_body("UserRegistered", user_id="u1"))


@pytest.mark.asyncio
async def test_account_deleted_without_email_fails(dispatcher: EventDispatcher):
    with pytest.raises(PermanentProcessingError):
        await dispatcher.process_body(_body("AccountDeleted", user_id="u1"))


@pytest.mark.asyncio
async def test_account_deleted_with_email(
    dispatcher: EventDispatcher, sender: ConsoleEmailSender
):
    await dispatcher.process_body(
        _body("AccountDeleted", user_id="u1", email="gone@example.com")
    )
    assert sender.sent[0].to == "gone@example.com"


@pytest.mark.asyncio
async def test_category_created_admin_fallback(
    dispatcher: EventDispatcher, sender: ConsoleEmailSender
):
    await dispatcher.process_body(
        _body("CategoryCreated", category_id="c1", name="Electronics")
    )
    assert "@" in sender.sent[0].to
    assert sender.sent[0].context["name"] == "Electronics"


@pytest.mark.asyncio
async def test_listing_status_changed(
    dispatcher: EventDispatcher, sender: ConsoleEmailSender
):
    await dispatcher.process_body(
        _body(
            "ListingStatusChanged",
            listing_id="l1",
            seller_id="s1",
            old_status="DRAFT",
            new_status="ACTIVE",
            email="seller@example.com",
        )
    )
    ctx = sender.sent[0].context
    assert ctx["old_status"] == "DRAFT"
    assert ctx["new_status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_transient_email_failure(dispatcher: EventDispatcher, sender: ConsoleEmailSender):
    sender.fail_next = True
    with pytest.raises(TransientProcessingError):
        await dispatcher.process_body(
            _body("UserRegistered", user_id="u1", email="user@example.com")
        )


@pytest.mark.asyncio
async def test_all_supported_types_registered():
    registry = default_job_registry()
    expected = {
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
    assert set(registry) == expected


def test_classify_error():
    assert classify_error(UnknownEventTypeError("x")) == "permanent"
    assert classify_error(TransientProcessingError("x")) == "transient"


@pytest.mark.asyncio
async def test_listing_jobs_need_email(dispatcher: EventDispatcher):
    with pytest.raises(PermanentProcessingError):
        await dispatcher.process_body(
            _body(
                "ListingCreated",
                listing_id="l1",
                seller_id="s1",
                title="Bike",
                status="DRAFT",
            )
        )
