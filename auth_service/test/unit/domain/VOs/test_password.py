import pytest

from src.domain.value_objects.password import Password
from src.exceptions import InvalidPasswordError

_MIN = 8
_MAX = 128


class TestPasswordBoundaries:
    def test_min_length_with_letter_and_digit(self):
        value = "abc12345"
        assert len(value) == _MIN
        assert Password(value).value == value

    def test_max_length_with_letter_and_digit(self):
        value = "a" * 63 + "1" + "a" * 64
        assert len(value) == _MAX
        assert Password(value).value == value

    def test_below_min_length_rejected(self):
        with pytest.raises(InvalidPasswordError):
            Password("abc1234")

    def test_above_max_length_rejected(self):
        value = "a" * 64 + "1" + "a" * 64
        assert len(value) == _MAX + 1
        with pytest.raises(InvalidPasswordError):
            Password(value)


class TestPasswordComposition:
    def test_missing_letter_rejected(self):
        with pytest.raises(InvalidPasswordError):
            Password("12345678")

    def test_missing_digit_rejected(self):
        with pytest.raises(InvalidPasswordError):
            Password("abcdefgh")

    def test_letter_and_digit_only_ok(self):
        assert Password("a1a1a1a1").value == "a1a1a1a1"

    def test_uppercase_letter_satisfies_letter_rule(self):
        assert Password("ABCDEFG1").value == "ABCDEFG1"

    def test_does_not_strip_whitespace(self):
        """The VO preserves input verbatim; whitespace counts toward length."""
        value = "  abc123  "
        assert len(value) == 10
        assert Password(value).value == value


class TestPasswordRejections:
    @pytest.mark.parametrize("value", [123, None, b"abc123", 1.5])
    def test_non_string_rejected(self, value):
        with pytest.raises(InvalidPasswordError):
            Password(value)  # type: ignore[arg-type]

    def test_empty_rejected(self):
        with pytest.raises(InvalidPasswordError):
            Password("")


class TestPasswordIdentity:
    def test_equality_and_hash(self):
        assert Password("abc12345") == Password("abc12345")
        assert hash(Password("abc12345")) == hash(Password("abc12345"))

    def test_inequality(self):
        assert Password("abc12345") != Password("abc123456")