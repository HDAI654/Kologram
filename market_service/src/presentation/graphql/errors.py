import logging
from graphql import GraphQLError
from src.exceptions import (
    CategoryAlreadyExistsError,
    CategoryInactiveError,
    CategoryNotFoundError,
    InvalidListingTransitionError,
    ListingNotEditableError,
    ListingNotFoundError,
    SellerMismatchError,
    VOError,
)


class ErrorManager:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def handle_error(self, exc: Exception, operation: str) -> GraphQLError:
        code = self._error_code(exc)

        if code == "INTERNAL_ERROR":
            self._logger.exception(
                "Unhandled error during %s", operation, exc_info=exc
            )
            return GraphQLError(
                "An internal error occurred",
                extensions={"code": code},
            )

        return GraphQLError(str(exc), extensions={"code": code})

    def _error_code(self, exc: Exception) -> str:
        if isinstance(exc, (ListingNotFoundError, CategoryNotFoundError)):
            return "NOT_FOUND"
        if isinstance(exc, SellerMismatchError):
            return "FORBIDDEN"
        if isinstance(
            exc,
            (
                InvalidListingTransitionError,
                ListingNotEditableError,
                CategoryInactiveError,
                CategoryAlreadyExistsError,
            ),
        ):
            return "CONFLICT"
        if isinstance(exc, VOError):
            return "VALIDATION_ERROR"
        if isinstance(exc, VOError):
            return "VALIDATION_ERROR"
        return "INTERNAL_ERROR"