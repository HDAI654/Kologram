"""Auth event jobs — email or temporary NOTHING."""

from __future__ import annotations

import logging
from typing import Any

from src.application.jobs.base import NotificationJob
from src.domain.events.auth_events import (
    AccountDeleted,
    UserLoggedIn,
    UserLoggedOut,
    UserRegistered,
    VerificationTokenCreated,
)
from src.domain.ports.email_sender import EmailSender

logger = logging.getLogger(__name__)


def _retry_send(sender: EmailSender, *, to: str, subject: str, body: str, max_attempts: int) -> None:
    """Send with up to max_attempts tries; last failure is logged and skipped."""
    from src.exceptions import EmailSendError

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            sender.send(to=to, subject=subject, body=body)
            return
        except EmailSendError as exc:
            last_error = exc
            logger.warning(
                "email send failed attempt=%s/%s to=%s error=%s",
                attempt,
                max_attempts,
                to,
                exc,
            )
    logger.error(
        "email skipped after %s attempts to=%s error=%s",
        max_attempts,
        to,
        last_error,
    )


class UserRegisteredJob(NotificationJob):
    event_type = "UserRegistered"

    def __init__(self, email_sender: EmailSender, max_attempts: int = 3) -> None:
        self._sender = email_sender
        self._max_attempts = max_attempts

    def handle(self, payload: dict[str, Any]) -> None:
        event = UserRegistered(
            user_id=str(payload.get("user_id", "")),
            email=str(payload.get("email", "")),
            occurred_at=payload.get("occurred_at"),
        )
        subject = "Welcome to Kologram"
        body = (
            f"Hi,\n\n"
            f"Your Kologram account is ready.\n"
            f"You signed up with {event.email}.\n\n"
            f"If this was not you, contact support.\n\n"
            f"— Kologram\n"
        )
        _retry_send(
            self._sender,
            to=event.email,
            subject=subject,
            body=body,
            max_attempts=self._max_attempts,
        )


class UserLoggedInJob(NotificationJob):
    event_type = "UserLoggedIn"

    def __init__(self, email_sender: EmailSender, max_attempts: int = 3) -> None:
        self._sender = email_sender
        self._max_attempts = max_attempts

    def handle(self, payload: dict[str, Any]) -> None:
        event = UserLoggedIn(
            user_id=str(payload.get("user_id", "")),
            email=str(payload.get("email", "")),
            session_id=str(payload.get("session_id", "")),
            device=str(payload.get("device", "unknown")),
            occurred_at=payload.get("occurred_at"),
        )
        subject = "New sign-in on your Kologram account"
        body = (
            f"Hi,\n\n"
            f"There was a new sign-in to your account.\n"
            f"Device: {event.device}\n\n"
            f"If this was you, no action is needed.\n"
            f"If not, reset your password and contact support.\n\n"
            f"— Kologram\n"
        )
        _retry_send(
            self._sender,
            to=event.email,
            subject=subject,
            body=body,
            max_attempts=self._max_attempts,
        )


class UserLoggedOutJob(NotificationJob):
    event_type = "UserLoggedOut"

    def __init__(self, email_sender: EmailSender, max_attempts: int = 3) -> None:
        self._sender = email_sender
        self._max_attempts = max_attempts

    def handle(self, payload: dict[str, Any]) -> None:
        # Logout payload has no email in some producers — prefer payload email if present.
        email = str(payload.get("email", "")).strip()
        event = UserLoggedOut(
            user_id=str(payload.get("user_id", "")),
            session_id=str(payload.get("session_id", "")),
            device=str(payload.get("device", "unknown")),
            occurred_at=payload.get("occurred_at"),
        )
        if not email:
            logger.info(
                "UserLoggedOut: no email on payload; skip send user_id=%s",
                event.user_id,
            )
            return
        subject = "You signed out of Kologram"
        body = (
            f"Hi,\n\n"
            f"You signed out successfully.\n"
            f"Device: {event.device}\n\n"
            f"If this was not you, reset your password.\n\n"
            f"— Kologram\n"
        )
        _retry_send(
            self._sender,
            to=email,
            subject=subject,
            body=body,
            max_attempts=self._max_attempts,
        )


class AccountDeletedJob(NotificationJob):
    event_type = "AccountDeleted"

    def handle(self, payload: dict[str, Any]) -> None:
        # Temporary NOTHING: no email / side effect until product defines retention messaging.
        event = AccountDeleted(
            user_id=str(payload.get("user_id", "")),
            occurred_at=payload.get("occurred_at"),
        )
        logger.info("AccountDeleted temporary NOTHING user_id=%s", event.user_id)


class VerifyEmailTokenJob(NotificationJob):
    """VerificationTokenCreated with token_type=verifyemail."""

    event_type = "VerificationTokenCreated"

    def __init__(self, email_sender: EmailSender, max_attempts: int = 3) -> None:
        self._sender = email_sender
        self._max_attempts = max_attempts

    def handle(self, payload: dict[str, Any]) -> None:
        event = VerificationTokenCreated(
            token=str(payload.get("token", "")),
            email=str(payload.get("email", "")),
            token_type=str(payload.get("token_type", "")),
            occurred_at=payload.get("occurred_at"),
        )
        subject = "Confirm your Kologram email"
        body = (
            f"Hi,\n\n"
            f"Use this code to confirm your email address:\n\n"
            f"  {event.token}\n\n"
            f"If you did not create a Kologram account, ignore this message.\n\n"
            f"— Kologram\n"
        )
        _retry_send(
            self._sender,
            to=event.email,
            subject=subject,
            body=body,
            max_attempts=self._max_attempts,
        )


class ResetPasswordTokenJob(NotificationJob):
    """VerificationTokenCreated with token_type=forget_pass_verify."""

    event_type = "VerificationTokenCreated"

    def __init__(self, email_sender: EmailSender, max_attempts: int = 3) -> None:
        self._sender = email_sender
        self._max_attempts = max_attempts

    def handle(self, payload: dict[str, Any]) -> None:
        event = VerificationTokenCreated(
            token=str(payload.get("token", "")),
            email=str(payload.get("email", "")),
            token_type=str(payload.get("token_type", "")),
            occurred_at=payload.get("occurred_at"),
        )
        subject = "Reset your Kologram password"
        body = (
            f"Hi,\n\n"
            f"Use this code to reset your password:\n\n"
            f"  {event.token}\n\n"
            f"If you did not ask for a reset, ignore this message.\n\n"
            f"— Kologram\n"
        )
        _retry_send(
            self._sender,
            to=event.email,
            subject=subject,
            body=body,
            max_attempts=self._max_attempts,
        )
