class InfrastructureError(Exception):
    """Base infrastructure error."""


# ===== DB =====
class DatabaseError(InfrastructureError):
    """Database operation failed."""


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to the database."""


class DatabaseOperationError(DatabaseError):
    """A database operation failed."""


class DatabaseTimeoutError(DatabaseError):
    """A database operation timed out."""


# ===== CACHE =====
class CacheError(InfrastructureError):
    """Cache operation failed."""


class CacheConnectionError(CacheError):
    """Failed to connect to the cache."""


class CacheTimeoutError(CacheError):
    """Cache operation timed out."""


class CacheOperationError(CacheError):
    """Generic cache operation failure."""


# ===== EVENT-BUS =====
class MessagingError(InfrastructureError):
    """Event bus operation failed."""


# ===== AUTH TOKEN =====
class TokenInfrastructureError(InfrastructureError):
    """Token encode/decode infrastructure failure."""
