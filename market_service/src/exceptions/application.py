"""Application-layer exceptions — use-case failures."""


class ApplicationError(Exception):
    """Base application error."""


class PermissionDeniedError(ApplicationError):
    """Caller is not allowed to perform the requested action."""


class SellerMismatchError(ApplicationError):
    """Authenticated user is not the listing seller."""


class InvalidSearchCriteriaError(ApplicationError):
    """Search / filter criteria are invalid."""
