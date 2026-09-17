import pytest

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.user_status import UserStatus
from src.exceptions import (
    InvalidEmailError,
    InvalidHashedPasswordError,
    InvalidUserIdError,
    InvalidUserStatusError,
)


@pytest.fixture
def credentials() -> dict[str, str]:
    return {
        "email": "user@example.com",
        "hashed_password": "$2b$12$abcdefghijklmnopqrstuv",
    }


class TestUserCreateDefaults:
    def test_generates_user_id(self, credentials):
        user = User.create(**credentials)

        assert isinstance(user.id, UserId)

    def test_normalizes_email(self, credentials):
        user = User.create(
            email="  User@Example.COM  ",
            hashed_password=credentials["hashed_password"],
        )

        assert isinstance(user.email, Email)
        assert user.email.value == "user@example.com"

    def test_wraps_hashed_password(self, credentials):
        user = User.create(**credentials)

        assert isinstance(user.hashed_password, HashedPassword)
        assert user.hashed_password.value == credentials["hashed_password"]

    def test_status_defaults_to_active(self, credentials):
        user = User.create(**credentials)

        assert isinstance(user.status, UserStatus)
        assert user.status.value == "ACTIVE"
        assert user.status.is_active is True

    def test_generated_user_ids_are_unique(self, credentials):
        a = User.create(**credentials)
        b = User.create(**credentials)

        assert a.id != b.id


class TestUserCreateExplicitFields:
    def test_explicit_user_id(self, credentials):
        user_id = UserId.generate().value
        user = User.create(**credentials, id=user_id)

        assert user.id.value == user_id

    def test_explicit_suspended_status(self, credentials):
        user = User.create(**credentials, status="SUSPENDED")

        assert user.status.value == "SUSPENDED"
        assert user.status.is_active is False

    def test_status_is_case_insensitive(self, credentials):
        user = User.create(**credentials, status="suspended")

        assert user.status.value == "SUSPENDED"


class TestUserCreateRejections:
    def test_invalid_email(self):
        with pytest.raises(InvalidEmailError):
            User.create(email="not-an-email", hashed_password="hash")

    def test_empty_hashed_password(self):
        with pytest.raises(InvalidHashedPasswordError):
            User.create(email="user@example.com", hashed_password="")

    def test_invalid_user_id(self, credentials):
        with pytest.raises(InvalidUserIdError):
            User.create(**credentials, id="not-a-uuid")

    def test_invalid_status(self, credentials):
        with pytest.raises(InvalidUserStatusError):
            User.create(**credentials, status="PENDING")


class TestUserChangePassword:
    def test_replaces_hash(self, credentials):
        user = User.create(**credentials)
        new_hash = HashedPassword("$2b$12$newhashnewhashnewhash")

        user.change_password(new_hash)

        assert user.hashed_password == new_hash

    def test_accepts_plain_string_hash_value(self, credentials):
        user = User.create(**credentials)
        replacement = HashedPassword("$2b$12$anothervalidhashvalue")

        user.change_password(replacement)

        assert user.hashed_password.value == "$2b$12$anothervalidhashvalue"


class TestUserConstructor:
    def test_direct_construction_defaults_to_active(self):
        user = User(
            id=UserId.generate(),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$2b$12$h"),
        )

        assert user.status.value == "ACTIVE"

    def test_direct_construction_with_suspended_status(self):
        user = User(
            id=UserId.generate(),
            email=Email("user@example.com"),
            hashed_password=HashedPassword("$2b$12$h"),
            status=UserStatus.suspended(),
        )

        assert user.status.value == "SUSPENDED"


class TestUserIdentity:
    def test_equal_when_all_attributes_match(self):
        user_id = UserId.generate().value
        a = User.create(
            email="user@example.com", hashed_password="$2b$12$h", id=user_id
        )
        b = User.create(
            email="user@example.com", hashed_password="$2b$12$h", id=user_id
        )

        assert a == b

    def test_not_equal_when_status_differs(self):
        user_id = UserId.generate().value
        a = User.create(
            email="user@example.com", hashed_password="$2b$12$h", id=user_id
        )
        b = User.create(
            email="user@example.com",
            hashed_password="$2b$12$h",
            id=user_id,
            status="SUSPENDED",
        )

        assert a != b
