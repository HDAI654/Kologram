import pytest

from src.domain.entities.listing import Listing
from src.domain.value_objects.listing_status import ListingStatus
from src.exceptions import (
    InvalidListingStatusError,
    InvalidListingTransitionError,
    ListingNotEditableError,
)

SELLER = "550e8400-e29b-41d4-a716-446655440000"
CATEGORY = "550e8400-e29b-41d4-a716-446655440001"


def _listing() -> Listing:
    return Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY,
        title="Vintage Camera",
        description="Fully working",
        price_amount="120.00",
        quantity=1,
        location="Istanbul",
    )


def test_valid_statuses() -> None:
    assert ListingStatus.draft().value == "DRAFT"
    assert ListingStatus.active().value == "ACTIVE"
    assert ListingStatus.sold().value == "SOLD"


def test_invalid_status_raises() -> None:
    with pytest.raises(InvalidListingStatusError):
        ListingStatus("UNKNOWN")


def test_draft_to_active_allowed() -> None:
    assert ListingStatus.draft().can_transition_to(ListingStatus.active()) is True


def test_sold_is_terminal() -> None:
    sold = ListingStatus.sold()
    assert sold.can_transition_to(ListingStatus.active()) is False
    assert sold.is_editable is False


def test_listing_publish_and_cancel() -> None:
    listing = _listing()
    assert listing.status.value == "DRAFT"
    listing.publish()
    assert listing.status.value == "ACTIVE"
    listing.cancel()
    assert listing.status.value == "CANCELLED"
    with pytest.raises(InvalidListingTransitionError):
        listing.publish()


def test_cannot_edit_sold_listing() -> None:
    listing = _listing()
    listing.publish()
    listing.mark_sold()
    with pytest.raises(ListingNotEditableError):
        listing.update_details(title="New title here")
