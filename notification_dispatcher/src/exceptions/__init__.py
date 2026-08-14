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

