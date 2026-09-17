import pytest

from src.domain.value_objects.title import Title
from src.exceptions import InvalidTitleError


class TestTitle:
    def test_min_length_allowed(self):
        assert Title("abc").value == "abc"

    def test_max_length_allowed(self):
        text = "a" * 120
        assert Title(text).value == text

    def test_below_min_rejected(self):
        with pytest.raises(InvalidTitleError):
            Title("ab")

    def test_above_max_rejected(self):
        with pytest.raises(InvalidTitleError):
            Title("a" * 121)

    def test_empty_rejected(self):
        with pytest.raises(InvalidTitleError):
            Title("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidTitleError):
            Title("   ")

    def test_normalizes_whitespace(self):
        assert Title("  Hello   World  ").value == "Hello World"

    def test_length_checked_after_normalization(self):
        with pytest.raises(InvalidTitleError):
            Title(" ab ")

    def test_rejects_non_string(self):
        for bad in (123, None, b"abc"):
            with pytest.raises(InvalidTitleError):
                Title(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert Title("Hello World") == Title("Hello World")
        assert hash(Title("Hello World")) == hash(Title("Hello World"))