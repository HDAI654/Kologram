"""Domain-layer exceptions — invariant violations and not-found."""


class DomainError(Exception):
    """Base domain error."""


# ===== Value objects =====

class VOError(DomainError):
    """Base value object error."""


class InvalidListingIdError(VOError):
    """Listing id is not a valid UUID v4."""


class InvalidCategoryIdError(VOError):
    """Category id is not a valid UUID v4."""


class InvalidUserIdError(VOError):
    """User / seller id is not a valid UUID v4."""


class InvalidMoneyError(VOError):
    """Money amount or currency is invalid."""


class InvalidQuantityError(VOError):
    """Quantity is invalid."""


class InvalidTitleError(VOError):
    """Listing title is invalid."""


class InvalidDescriptionError(VOError):
    """Listing description is invalid."""


class InvalidLocationError(VOError):
    """Location string is invalid."""


class InvalidListingStatusError(VOError):
    """Listing status value is not recognized."""


class InvalidCategoryNameError(VOError):
    """Category name is invalid."""


class InvalidImageUrlError(VOError):
    """Image URL is invalid."""


class InvalidSortOrderError(VOError):
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
