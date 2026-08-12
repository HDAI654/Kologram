import pytest

from src.domain.value_objects.location import Location
from src.exceptions import InvalidLocationError


def test_valid() -> None:
    assert Location("  New York  ").value == "New York"


def test_invalid() -> None:
    with pytest.raises(InvalidLocationError):
        Location("")
    with pytest.raises(InvalidLocationError):
        Location("x" * 201)
