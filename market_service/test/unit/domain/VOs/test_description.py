import pytest

from src.domain.value_objects.description import Description
from src.exceptions import InvalidDescriptionError


class TestDescription:
    def test_empty_allowed(self):
        assert Description("").value == ""

    def test_whitespace_only_normalized_to_empty(self):
        assert Description("    ").value == ""

    def test_valid_text(self):
        assert Description("Hello world").value == "Hello world"

    def test_strips_leading_and_trailing_whitespace(self):
        assert Description("  hello  ").value == "hello"

    def test_preserves_internal_whitespace(self):
        # Description only strips; it does not collapse internal whitespace.
        assert Description("a   b\nc").value == "a   b\nc"

    def test_max_length_allowed(self):
        text = "a" * 5000
        assert Description(text).value == text

    def test_over_max_length_rejected(self):
        with pytest.raises(InvalidDescriptionError):
            Description("a" * 5001)

    def test_length_checked_after_strip(self):
        text = "a" * 5000
        assert Description(f"  {text}  ").value == text

    def test_rejects_non_string(self):
        for bad in (123, None, b"x"):
            with pytest.raises(InvalidDescriptionError):
                Description(bad)  # type: ignore[arg-type]

    def test_equality_and_hash(self):
        assert Description("x") == Description("x")
        assert hash(Description("x")) == hash(Description("x"))
