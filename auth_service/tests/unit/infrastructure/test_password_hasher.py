import pytest

from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.password import Password
from src.infrastructure.security.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)


@pytest.fixture(scope="module")
def hasher() -> BcryptPasswordHasher:
    return BcryptPasswordHasher()


class TestHash:
    def test_returns_hashed_password_vo(self, hasher):
        result = hasher.hash(Password("password1"))
        assert isinstance(result, HashedPassword)

    def test_hash_looks_like_bcrypt(self, hasher):
        result = hasher.hash(Password("password1"))
        assert result.value.startswith("$2")

    def test_same_input_produces_different_hashes(self, hasher):
        a = hasher.hash(Password("password1"))
        b = hasher.hash(Password("password1"))
        assert a.value != b.value


class TestVerify:
    def test_correct_password_verifies(self, hasher):
        hashed = hasher.hash(Password("password1"))
        assert hasher.verify("password1", hashed) is True

    def test_wrong_password_fails(self, hasher):
        hashed = hasher.hash(Password("password1"))
        assert hasher.verify("password2", hashed) is False

    def test_returns_false_on_malformed_hash(self, hasher):
        bad = HashedPassword("not-a-bcrypt-hash")
        assert hasher.verify("password1", bad) is False

    def test_case_sensitive(self, hasher):
        hashed = hasher.hash(Password("Password1"))
        assert hasher.verify("password1", hashed) is False