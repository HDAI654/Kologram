"""Infrastructure-layer exceptions — technical failures."""


class InfrastructureError(Exception):
    """Base infrastructure error."""


class DatabaseError(InfrastructureError):
    """Database operation failed."""


class DatabaseConnectionError(DatabaseError):
    """Failed to connect to the database."""


class DatabaseOperationError(DatabaseError):
    """A database operation failed."""


class DatabaseTimeoutError(DatabaseError):
    """A database operation timed out."""


class MessagingError(InfrastructureError):
    """Event bus operation failed."""


class MessagingConnectionError(MessagingError):
    """Failed to connect to the message bus."""


class CacheError(InfrastructureError):
    """Cache operation failed."""


class CacheConnectionError(CacheError):
    """Failed to connect to the cache."""


class CacheOperationError(CacheError):
    """Generic cache operation failure."""
