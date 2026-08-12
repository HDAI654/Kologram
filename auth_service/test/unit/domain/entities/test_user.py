import pytest
from src.domain.entities.user import User
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_status import UserStatus
from src.exceptions import (
    InvalidUserIdError,
    InvalidEmailError,
    InvalidHashedPasswordError,
    InvalidUserStatusError,
)


class TestUser:
    def test_init_valid_default_status(self):
        user_id = UserId("3bb6a3ca-66dc-440e-8d11-d8cca7ad779a")
        email = Email("test@example.com")
        hashed = HashedPassword("$2b$12$abc...")
        user = User(user_id, email, hashed)
        assert user.id == user_id
        assert user.email == email
        assert user.hashed_password == hashed
        assert user.status == UserStatus.active()

    def test_init_with_custom_status(self):
        user_id = UserId("3bb6a3ca-66dc-440e-8d11-d8cca7ad779b")
        email = Email("test@example.com")
        hashed = HashedPassword("$2b$12$abc...")
        status = UserStatus.suspended()
        user = User(user_id, email, hashed, status)
        assert user.status == status

    def test_create_defaults(self):
        email_str = "test@example.com"
        hashed_str = "$2b$12$abc..."
        user = User.create(email=email_str, hashed_password=hashed_str)
        assert isinstance(user.id, UserId)
        assert user.email.value == email_str
        assert user.hashed_password.value == hashed_str
        assert user.status == UserStatus.active()

    def test_create_with_custom_id_and_status(self):
        id_str = "3bb6a3ca-66dc-440e-8d11-d8cca7ad779c"
        email_str = "test@example.com"
        hashed_str = "$2b$12$abc..."
        status_str = "SUSPENDED"
        user = User.create(
            email=email_str,
            hashed_password=hashed_str,
            id=id_str,
            status=status_str,
        )
        assert user.id.value == id_str
        assert user.status == UserStatus.suspended()

    def test_create_invalid_id(self):
        with pytest.raises(InvalidUserIdError):
            User.create(
                email="test@example.com", hashed_password="hash", id="not-a-uuid"
            )

    def test_create_invalid_email(self):
        with pytest.raises(InvalidEmailError):
            User.create(email="invalid", hashed_password="hash")

    def test_create_invalid_hashed_password(self):
        with pytest.raises(InvalidHashedPasswordError):
            User.create(email="test@example.com", hashed_password="")

    def test_create_invalid_status(self):
        with pytest.raises(InvalidUserStatusError):
            User.create(
                email="test@example.com",
                hashed_password="hash",
                status="INACTIVE",
            )

    def test_change_password(self):
        user_id = UserId("3bb6a3ca-66dc-440e-8d11-d8cca7ad779d")
        email = Email("test@example.com")
        old_hash = HashedPassword("old_hash")
        user = User(user_id, email, old_hash)
        new_hash = HashedPassword("new_hash")
        user.change_password(new_hash)
        assert user.hashed_password == new_hash
