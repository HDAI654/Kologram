import pytest

from src.domain.value_objects.title import Title
from src.exceptions import InvalidTitleError


def test_title_normalizes_whitespace() -> None:
    assert Title("  Hello   World  ").value == "Hello World"


def test_title_too_short() -> None:
    with pytest.raises(InvalidTitleError):
        Title("ab")


def test_title_too_long() -> None:
    with pytest.raises(InvalidTitleError):
        Title("x" * 121)
