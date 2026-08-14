"""Notification jobs for auth-service events."""

from __future__ import annotations

from src.application.jobs.base import NotificationJob, base_context, resolve_recipient
from src.domain.events.envelope import IncomingEvent, require_fields
from src.domain.notifications.email_message import EmailMessage, NotificationSpec


class AccountDeletedJob(NotificationJob):
    event_type = "AccountDeleted"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Confirm the user's account was deleted.",
            recipient_source="event.email (preferred) or cannot notify without email",
            subject_intent="Account deletion confirmation",
            required_context_keys=("user_id", "occurred_at"),
            optional_context_keys=("email",),
            security_notes="Do not imply recoverability unless product supports it.",
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "user_id")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="account_deleted",
            template_key="account_deleted",
            context=base_context(
                event,
                user_id=event.get("user_id"),
            ),
            is_security_sensitive=True,
        )


class UserLoggedInJob(NotificationJob):
    event_type = "UserLoggedIn"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Security alert: successful login.",
            recipient_source="event.email",
            subject_intent="New sign-in to your account",
            required_context_keys=("user_id", "email", "occurred_at"),
            optional_context_keys=("session_id", "device", "role"),
            security_notes=(
                "Instruct user to revoke session via profile if login was not them. "
                "Do not log session_id at info level in application logs."
            ),
            is_security_sensitive=True,
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "user_id", "email")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="user_logged_in",
            template_key="user_logged_in",
            context=base_context(
                event,
                user_id=event.get("user_id"),
                email=event.get("email"),
                session_id=event.get("session_id"),
                device=event.get("device"),
                role=event.get("role"),
                guidance="If this was not you, open your account security settings "
                "and revoke the session.",
            ),
            is_security_sensitive=True,
        )


class UserLoggedOutJob(NotificationJob):
    event_type = "UserLoggedOut"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Informational logout confirmation.",
            recipient_source="event.email if present",
            subject_intent="You signed out",
            required_context_keys=("user_id", "occurred_at"),
            optional_context_keys=("session_id", "device", "email"),
            security_notes="Avoid alarmist wording.",
            is_security_sensitive=False,
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "user_id")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="user_logged_out",
            template_key="user_logged_out",
            context=base_context(
                event,
                user_id=event.get("user_id"),
                session_id=event.get("session_id"),
                device=event.get("device"),
            ),
        )


class UserRegisteredJob(NotificationJob):
    event_type = "UserRegistered"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Welcome / registration confirmation.",
            recipient_source="event.email",
            subject_intent="Welcome — account created",
            required_context_keys=("user_id", "email", "occurred_at"),
            security_notes="Never include passwords or hashes.",
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "user_id", "email")
        to = resolve_recipient(event)
        return EmailMessage(
            to=to,
            subject_key="user_registered",
            template_key="user_registered",
            context=base_context(
                event,
                user_id=event.get("user_id"),
                email=event.get("email"),
            ),
        )


class VerificationTokenCreatedJob(NotificationJob):
    event_type = "VerificationTokenCreated"

    def spec(self) -> NotificationSpec:
        return NotificationSpec(
            event_type=self.event_type,
            purpose="Deliver verification / reset token to the user.",
            recipient_source="event.email",
            subject_intent="Your verification code / token",
            required_context_keys=("email", "token", "token_type", "occurred_at"),
            security_notes=(
                "Include token in email only. Never log the token. "
                "Warn user to ignore if they did not request it."
            ),
            is_security_sensitive=True,
        )

    def build(self, event: IncomingEvent) -> EmailMessage:
        require_fields(event, "email", "token", "token_type")
        to = resolve_recipient(event)
        # Token is intentional in context for the email renderer only.
        return EmailMessage(
            to=to,
            subject_key="verification_token_created",
            template_key="verification_token_created",
            context=base_context(
                event,
                email=event.get("email"),
                token=event.get("token"),
                token_type=event.get("token_type"),
                security_warning="Ignore this message if you did not request it.",
            ),
            is_security_sensitive=True,
        )
