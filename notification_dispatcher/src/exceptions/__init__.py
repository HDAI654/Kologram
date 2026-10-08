"""Service exceptions."""


class ApplicationError(Exception):
    """Base application error."""


class UnknownEventTypeError(ApplicationError):
    """No handler registered for the event type."""


class InfrastructureError(Exception):
    """Base infrastructure error."""


class EmailSendError(InfrastructureError):
    """Outbound email failed."""


class MessagingError(InfrastructureError):
    """Broker / consumer failure."""
