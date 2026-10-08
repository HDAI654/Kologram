from __future__ import annotations

from typing import Any

import pytest

from src.application.dispatcher import Dispatcher
from src.application.jobs.auth_jobs import (
    AccountDeletedJob,
    UserLoggedInJob,
    UserLoggedOutJob,
    UserRegisteredJob,
    VerifyEmailTokenJob,
    ResetPasswordTokenJob,
)
from src.application.jobs.market_jobs import ListingCreatedJob
from src.application.jobs.chat_jobs import MessageSentJob
from src.domain.ports.email_sender import EmailSender
from src.domain.ports.idempotency_store import IdempotencyStore
from src.exceptions import EmailSendError, UnknownEventTypeError


class FakeEmail(EmailSender):
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self.fail_times = 0

    def send(self, *, to: str, subject: str, body: str) -> None:
        if self.fail_times > 0:
            self.fail_times -= 1
            raise EmailSendError("boom")
        self.sent.append((to, subject, body))


class MemoryIdem(IdempotencyStore):
    def __init__(self) -> None:
        self.keys: set[str] = set()

    def already_processed(self, key: str) -> bool:
        return key in self.keys

    def mark_processed(self, key: str) -> None:
        self.keys.add(key)


def _dispatcher(email: FakeEmail, idem: MemoryIdem) -> Dispatcher:
    return Dispatcher(
        {
            "UserRegistered": UserRegisteredJob(email, max_attempts=3),
            "UserLoggedIn": UserLoggedInJob(email, max_attempts=3),
            "UserLoggedOut": UserLoggedOutJob(email, max_attempts=3),
            "AccountDeleted": AccountDeletedJob(),
            "ListingCreated": ListingCreatedJob(),
            "MessageSent": MessageSentJob(),
        },
        idem,
        verification_jobs={
            "verifyemail": VerifyEmailTokenJob(email, max_attempts=3),
            "forget_pass_verify": ResetPasswordTokenJob(email, max_attempts=3),
        },
    )


def test_user_registered_sends_welcome() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k1",
        event_type="UserRegistered",
        payload={"user_id": "u1", "email": "a@b.com"},
    )
    assert len(email.sent) == 1
    assert email.sent[0][0] == "a@b.com"
    assert "Welcome" in email.sent[0][1]


def test_user_logged_in_includes_device() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k2",
        event_type="UserLoggedIn",
        payload={
            "user_id": "u1",
            "email": "a@b.com",
            "session_id": "s1",
            "device": "iPhone",
        },
    )
    assert "iPhone" in email.sent[0][2]


def test_account_deleted_nothing() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k3",
        event_type="AccountDeleted",
        payload={"user_id": "u1"},
    )
    assert email.sent == []


def test_listing_created_nothing() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k4",
        event_type="ListingCreated",
        payload={"listing_id": "l1"},
    )
    assert email.sent == []


def test_message_sent_nothing() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k5",
        event_type="MessageSent",
        payload={"message_id": "m1"},
    )
    assert email.sent == []


def test_verifyemail_token() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k6",
        event_type="VerificationTokenCreated",
        payload={
            "email": "a@b.com",
            "token": "tok-1",
            "token_type": "verifyemail",
        },
    )
    assert "tok-1" in email.sent[0][2]
    assert "Confirm" in email.sent[0][1]


def test_reset_token() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="k7",
        event_type="VerificationTokenCreated",
        payload={
            "email": "a@b.com",
            "token": "tok-2",
            "token_type": "forget_pass_verify",
        },
    )
    assert "tok-2" in email.sent[0][2]
    assert "Reset" in email.sent[0][1]


def test_idempotency_skips_second() -> None:
    email = FakeEmail()
    idem = MemoryIdem()
    d = _dispatcher(email, idem)
    d.dispatch(
        idempotency_key="same",
        event_type="UserRegistered",
        payload={"user_id": "u1", "email": "a@b.com"},
    )
    d.dispatch(
        idempotency_key="same",
        event_type="UserRegistered",
        payload={"user_id": "u1", "email": "a@b.com"},
    )
    assert len(email.sent) == 1


def test_retry_then_success() -> None:
    email = FakeEmail()
    email.fail_times = 2
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="r1",
        event_type="UserRegistered",
        payload={"user_id": "u1", "email": "a@b.com"},
    )
    assert len(email.sent) == 1


def test_retry_exhausted_skips() -> None:
    email = FakeEmail()
    email.fail_times = 10
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="r2",
        event_type="UserRegistered",
        payload={"user_id": "u1", "email": "a@b.com"},
    )
    assert email.sent == []


def test_unknown_event_raises() -> None:
    d = _dispatcher(FakeEmail(), MemoryIdem())
    with pytest.raises(UnknownEventTypeError):
        d.dispatch(idempotency_key="x", event_type="Nope", payload={})


def test_user_logged_out_with_email() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="lo1",
        event_type="UserLoggedOut",
        payload={
            "user_id": "u1",
            "email": "a@b.com",
            "session_id": "s1",
            "device": "web",
        },
    )
    assert len(email.sent) == 1
    assert "signed out" in email.sent[0][2].lower() or "sign out" in email.sent[0][2].lower()


def test_user_logged_out_without_email_skips() -> None:
    email = FakeEmail()
    d = _dispatcher(email, MemoryIdem())
    d.dispatch(
        idempotency_key="lo2",
        event_type="UserLoggedOut",
        payload={"user_id": "u1", "session_id": "s1", "device": "web"},
    )
    assert email.sent == []
