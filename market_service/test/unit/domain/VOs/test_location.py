import pytest

from src.domain.value_objects.location import Location
from src.exceptions import InvalidLocationError


class TestLocation:
    def test_valid(self):
        assert Location("New York").value == "New York"

    def test_normalizes_whitespace(self):
        assert Location("  New   York  ").value == "New York"

    def test_empty_rejected(self):
        with pytest.raises(InvalidLocationError):
            Location("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidLocationError):
            Location("   ")

    def test_max_length_allowed(self):
        text = "a" * 200
        assert Location(text).value == text

    def test_over_max_length_rejected(self):
        with pytest.raises(InvalidLocationError):
            Location("a" * 201)

    def test_length_checked_after_normalization(self):
        text = "a" * 200
        assert Location(f"  {text}  ").value == text

    def test_rejects_non_string(self):
        for bad in (123, None, b"NYC"):
            with pytest.raises(InvalidLocationError):
                Location(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert Location("NYC") == Location("NYC")
        assert hash(Location("NYC")) == hash(Location("NYC"))
