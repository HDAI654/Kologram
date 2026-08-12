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

class InvalidEmailError(DomainError):
    """Email format is invalid."""

    pass

class InvalidPasswordError(DomainError):
    """Password does not meet domain strength rules."""

    pass

class InvalidHashedPasswordError(DomainError):
    """Hashed password payload is invalid."""

    pass

class InvalidDeviceError(DomainError):
    """Device identifier is invalid."""

    pass

class InvalidDateError(DomainError):
    """Date value is invalid."""

    pass

class InvalidUserStatusError(DomainError):
    """UserStatus value is not recognized."""

    pass

class InvalidVerificationTokenError(DomainError):
    """Verification token is not a valid UUID v4."""

    pass
