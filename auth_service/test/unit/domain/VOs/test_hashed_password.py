import pytest
from src.domain.value_objects.hashed_password import HashedPassword
from src.exceptions import InvalidHashedPasswordError


class TestHashedPassword:
    def test_not_str(self):
        with pytest.raises(InvalidHashedPasswordError):
            HashedPassword(123)
            HashedPassword(None)
            HashedPassword([])

    def test_empty_str(self):
        with pytest.raises(InvalidHashedPasswordError):
            HashedPassword("")
            HashedPassword(" ")
            HashedPassword("    ")

    def test_strip(self):
        pw = "  some_hash  "
        vo = HashedPassword(pw)
        assert vo.value == "some_hash"

    def test_any_non_empty_string_accepted(self):
        vo = HashedPassword("$2b$12$abc...")
        assert vo.value == "$2b$12$abc..."
