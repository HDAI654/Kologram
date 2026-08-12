class DomainError(Exception):
    """Base domain error."""

    pass


# ===== VOs =====
class InvalidUserIdError(DomainError):
    """User id is not a valid UUID v4."""

    pass


class InvalidSessionIdError(DomainError):
    """Session id is not a valid UUID v4."""

    pass
