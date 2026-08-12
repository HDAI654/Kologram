class ApplicationError(Exception):
    """Base application error."""

    pass


class EmailBlockedError(ApplicationError):
    """Email address is on the blocklist."""


class InvalidEmailOrPasswordError(ApplicationError):
    """Login failed (generic message — do not leak which field failed)."""


class DeviceMismatchError(ApplicationError):
    """Request device does not match the session device claim."""


class PermissionDeniedError(ApplicationError):
    """Caller is not allowed to perform the requested action."""


class AccountSuspendedError(ApplicationError):
    """The user account is suspended; actions requiring an active status are blocked."""
