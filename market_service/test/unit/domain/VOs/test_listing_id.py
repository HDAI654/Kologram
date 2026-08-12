import pytest

from src.domain.value_objects.listing_id import ListingId
from src.exceptions import InvalidListingIdError


def test_generate_is_uuid_v4() -> None:
    lid = ListingId.generate()
    assert len(lid.value) == 36
    assert ListingId(lid.value) == lid


def test_invalid_uuid_raises() -> None:
    with pytest.raises(InvalidListingIdError):
        ListingId("not-a-uuid")


def test_empty_raises() -> None:
    with pytest.raises(InvalidListingIdError):
        ListingId("")


def test_equality() -> None:
    raw = "550e8400-e29b-41d4-a716-446655440000"
    assert ListingId(raw) == ListingId(raw)
