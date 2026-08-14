"""Layered exceptions for notification-dispatcher."""

from __future__ import annotations

# ==== BASE ERRORS =====
# ======================
class DomainError(Exception):
    """Business / invariant violation."""


class ApplicationError(Exception):
    """Use-case failure."""

class InfrastructureError(Exception):
    """Technical failure."""
# ======================

class PermanentProcessingError(ApplicationError):
    """Message must not be retried (malformed, unknown type, missing recipient)."""

class InvalidEventError(PermanentProcessingError):
    """Event payload cannot be interpreted safely."""

class TransientProcessingError(ApplicationError):
    """Temporary failure; message may be requeued."""

class MessagingError(InfrastructureError):
    """RabbitMQ / transport failure."""

class EmailDeliveryError(InfrastructureError):
    """Email provider failure (may be transient)."""

class UnknownEventTypeError(PermanentProcessingError):
    """Event type is not supported by this dispatcher version."""

class MissingRecipientError(PermanentProcessingError):
    """No resolvable recipient email for the notification."""