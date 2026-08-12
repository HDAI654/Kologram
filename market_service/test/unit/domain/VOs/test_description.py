import pytest

from src.domain.value_objects.description import Description
from src.exceptions import InvalidDescriptionError


def test_empty_and_valid() -> None:
    assert Description("").value == ""
    assert Description("  Nice item  ").value == "Nice item"


def test_too_long() -> None:
    with pytest.raises(InvalidDescriptionError):
        Description("x" * 5001)
