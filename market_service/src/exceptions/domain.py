"""Domain-layer exceptions — invariant violations and not-found."""


class DomainError(Exception):
    """Base domain error."""


# ===== Value objects =====


class InvalidListingIdError(DomainError):
    """Listing id is not a valid UUID v4."""


class InvalidCategoryIdError(DomainError):
    """Category id is not a valid UUID v4."""


class InvalidUserIdError(DomainError):
    """User / seller id is not a valid UUID v4."""


class InvalidMoneyError(DomainError):
    """Money amount or currency is invalid."""


class InvalidQuantityError(DomainError):
    """Quantity is invalid."""


class InvalidTitleError(DomainError):
    """Listing title is invalid."""


class InvalidDescriptionError(DomainError):
    """Listing description is invalid."""


class InvalidLocationError(DomainError):
    """Location string is invalid."""


class InvalidListingStatusError(DomainError):
    """Listing status value is not recognized."""


class InvalidCategoryNameError(DomainError):
    """Category name is invalid."""


class InvalidImageUrlError(DomainError):
    """Image URL is invalid."""


class InvalidSortOrderError(DomainError):
    """Image sort order is invalid."""


# ===== Aggregates / business rules =====


class ListingNotFoundError(DomainError):
    """Listing aggregate was not found."""


class CategoryNotFoundError(DomainError):
    """Category aggregate was not found."""


class CategoryAlreadyExistsError(DomainError):
    """A category with the same name already exists."""


class ListingNotEditableError(DomainError):
    """Listing cannot be modified in its current status."""


class InvalidListingTransitionError(DomainError):
    """Requested status transition is not allowed."""


class CategoryInactiveError(DomainError):
    """Category is inactive and cannot accept new listings."""
