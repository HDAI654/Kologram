import pytest

from src.domain.value_objects.hashed_password import HashedPassword
from src.exceptions import InvalidHashedPasswordError


class TestHashedPassword:
    def test_accepts_any_non_empty_string(self):
        assert HashedPassword("$2b$12$abc").value == "$2b$12$abc"

    def test_strips_surrounding_whitespace(self):
        assert HashedPassword("  $2b$12$abc  ").value == "$2b$12$abc"

    def test_preserves_internal_content(self):
        value = "$2b$12$abcdefghijklmnopqrstuv"
        assert HashedPassword(value).value == value

    def test_empty_string_rejected(self):
        with pytest.raises(InvalidHashedPasswordError):
            HashedPassword("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(InvalidHashedPasswordError):
            HashedPassword("   ")

    @pytest.mark.parametrize("value", [123, None, b"hash", 1.5])
    def test_non_string_rejected(self, value):
        with pytest.raises(InvalidHashedPasswordError):
            HashedPassword(value)  # type: ignore[arg-type]

    def test_does_not_validate_hash_format(self):
        """Opaque by contract; only non-emptiness is enforced."""
        assert HashedPassword("not-a-real-hash").value == "not-a-real-hash"

    def test_equality_and_hash(self):
        assert HashedPassword("h") == HashedPassword("h")
        assert hash(HashedPassword("h")) == hash(HashedPassword("h"))