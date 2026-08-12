"""Map domain/application exceptions to GraphQL-friendly errors."""

from __future__ import annotations

from graphql import GraphQLError

from src.exceptions import (
    CategoryAlreadyExistsError,
    CategoryInactiveError,
    CategoryNotFoundError,
    InvalidCategoryNameError,
    InvalidDescriptionError,
    InvalidListingStatusError,
    InvalidListingTransitionError,
    InvalidLocationError,
    InvalidMoneyError,
    InvalidQuantityError,
    InvalidTitleError,
    ListingNotEditableError,
    ListingNotFoundError,
    SellerMismatchError,
)

_NOT_FOUND = (
    ListingNotFoundError,
    CategoryNotFoundError,
)
_FORBIDDEN = (SellerMismatchError,)
_CONFLICT = (
    InvalidListingTransitionError,
    ListingNotEditableError,
    CategoryInactiveError,
    CategoryAlreadyExistsError,
)
_VALIDATION = (
    InvalidTitleError,
    InvalidDescriptionError,
    InvalidMoneyError,
    InvalidQuantityError,
    InvalidLocationError,
    InvalidListingStatusError,
    InvalidCategoryNameError,
)


def raise_graphql_error(exc: Exception) -> None:
    """Raise a GraphQLError with a stable extension code for clients."""
    if isinstance(exc, _NOT_FOUND):
        raise GraphQLError(str(exc), extensions={"code": "NOT_FOUND"}) from exc
    if isinstance(exc, _FORBIDDEN):
        raise GraphQLError(str(exc), extensions={"code": "FORBIDDEN"}) from exc
    if isinstance(exc, _CONFLICT):
        raise GraphQLError(str(exc), extensions={"code": "CONFLICT"}) from exc
    if isinstance(exc, _VALIDATION):
        raise GraphQLError(str(exc), extensions={"code": "VALIDATION_ERROR"}) from exc
    raise GraphQLError(str(exc), extensions={"code": "INTERNAL_ERROR"}) from exc
