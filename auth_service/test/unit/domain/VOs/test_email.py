import pytest

from src.domain.value_objects.email import Email
from src.exceptions import InvalidEmailError

_MAX_LEN = 254


class TestEmailNormalization:
    def test_lowercases(self):
        assert Email("User@Example.COM").value == "user@example.com"

    def test_strips_whitespace(self):
        assert Email("  user@example.com  ").value == "user@example.com"

    def test_strip_then_lowercase(self):
        assert Email("  User@Example.com  ").value == "user@example.com"

    def test_minimal_valid_address(self):
        assert Email("a@b.c").value == "a@b.c"


class TestEmailBoundaries:
    def test_max_length_boundary(self):
        value = "a" * 240 + "@" + "b" * 9 + "." + "c" * 3  # exactly 254
        assert len(value) == _MAX_LEN
        assert Email(value).value == value

    def test_over_max_length_rejected(self):
        value = "a" * 241 + "@" + "b" * 9 + "." + "c" * 3  # exactly 255
        assert len(value) == _MAX_LEN + 1
        with pytest.raises(InvalidEmailError):
            Email(value)


class TestEmailRejections:
    @pytest.mark.parametrize(
        "value",
        [
            "",
            "   ",
            "user",
            "@example.com",
            "user@",
            "user@example",  # no dot in domain
            "user name@example.com",  # internal space
            "user@@example.com",
            "user@exa mple.com",
        ],
    )
    def test_invalid_format_rejected(self, value):
        with pytest.raises(InvalidEmailError):
            Email(value)

    @pytest.mark.parametrize("value", [123, None, b"a@b.c", 1.5])
    def test_non_string_rejected(self, value):
        with pytest.raises(InvalidEmailError):
            Email(value)  # type: ignore[arg-type]


class TestEmailIdentity:
    def test_equality_and_hash_case_insensitive(self):
        assert Email("User@Example.com") == Email("user@example.com")
        assert hash(Email("User@Example.com")) == hash(Email("user@example.com"))

    def test_inequality(self):
        assert Email("a@b.c") != Email("x@y.z")
