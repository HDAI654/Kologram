import pytest

from src.domain.value_objects.listing_status import ListingStatus
from src.exceptions import InvalidListingStatusError

ALL_STATUSES = ("DRAFT", "ACTIVE", "SOLD", "EXPIRED", "CANCELLED", "SUSPENDED")

VALID_TRANSITIONS = {
    "DRAFT": {"ACTIVE", "CANCELLED"},
    "ACTIVE": {"SOLD", "EXPIRED", "CANCELLED", "SUSPENDED"},
    "SOLD": set(),
    "EXPIRED": {"ACTIVE", "CANCELLED"},
    "CANCELLED": set(),
    "SUSPENDED": {"ACTIVE", "CANCELLED"},
}

EDITABLE_STATUSES = {"DRAFT", "ACTIVE", "EXPIRED"}


class TestListingStatusConstruction:
    @pytest.mark.parametrize("value", ALL_STATUSES)
    def test_valid_statuses(self, value):
        assert ListingStatus(value).value == value

    @pytest.mark.parametrize("value", ALL_STATUSES)
    def test_case_insensitive_and_whitespace(self, value):
        assert ListingStatus(f"  {value.lower()}  ").value == value

    def test_invalid_value_rejected(self):
        with pytest.raises(InvalidListingStatusError):
            ListingStatus("UNKNOWN")

    def test_empty_rejected(self):
        with pytest.raises(InvalidListingStatusError):
            ListingStatus("")

    def test_rejects_non_string(self):
        for bad in (123, None, b"DRAFT"):
            with pytest.raises(InvalidListingStatusError):
                ListingStatus(bad)  # type: ignore[arg-type]

    def test_class_constructors(self):
        assert ListingStatus.draft().value == "DRAFT"
        assert ListingStatus.active().value == "ACTIVE"
        assert ListingStatus.sold().value == "SOLD"
        assert ListingStatus.expired().value == "EXPIRED"
        assert ListingStatus.cancelled().value == "CANCELLED"
        assert ListingStatus.suspended().value == "SUSPENDED"


class TestListingStatusTransitions:
    @pytest.mark.parametrize("source", ALL_STATUSES)
    @pytest.mark.parametrize("target", ALL_STATUSES)
    def test_can_transition_to(self, source, target):
        expected = target in VALID_TRANSITIONS[source]
        assert (
            ListingStatus(source).can_transition_to(ListingStatus(target)) is expected
        )


class TestListingStatusEditability:
    @pytest.mark.parametrize("value", ALL_STATUSES)
    def test_is_editable(self, value):
        assert ListingStatus(value).is_editable is (value in EDITABLE_STATUSES)


class TestListingStatusIdentity:
    def test_equality_and_hash(self):
        assert ListingStatus("DRAFT") == ListingStatus("draft")
        assert hash(ListingStatus("DRAFT")) == hash(ListingStatus("draft"))
