from src.domain.value_objects.password import Password
from src.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher


def test_hash_and_verify_roundtrip() -> None:
    hasher = BcryptPasswordHasher()
    hashed = hasher.hash(Password("Secret12"))
    assert hasher.verify("Secret12", hashed) is True
    assert hasher.verify("wrong-pass", hashed) is False
