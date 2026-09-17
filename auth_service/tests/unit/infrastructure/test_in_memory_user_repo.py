import pytest

from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.user_id import UserId
from src.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


class TestAdd:
    async def test_stores_by_id_and_email(self, repo, make_user):
        user = make_user(email="user@example.com")
        await repo.add(user)
        assert await repo.get_by_id(user.id) is user
        assert await repo.get_by_email(user.email) is user

    async def test_duplicate_email_raises(self, repo, make_user):
        await repo.add(make_user(email="user@example.com"))
        with pytest.raises(UserAlreadyExistsError):
            await repo.add(make_user(email="user@example.com"))

    async def test_duplicate_id_raises(self, repo, make_user):
        user = make_user(email="a@example.com")
        await repo.add(user)
        with pytest.raises(UserAlreadyExistsError):
            await repo.add(
                make_user(email="b@example.com", user_id=user.id.value)
            )


class TestGetById:
    async def test_returns_stored_user(self, repo, make_user):
        user = make_user()
        await repo.add(user)
        assert await repo.get_by_id(user.id) is user

    async def test_missing_raises(self, repo):
        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(UserId.generate())


class TestGetByEmail:
    async def test_returns_stored_user(self, repo, make_user):
        user = make_user(email="user@example.com")
        await repo.add(user)
        assert await repo.get_by_email(Email("user@example.com")) is user

    async def test_missing_raises(self, repo):
        with pytest.raises(UserNotFoundError):
            await repo.get_by_email(Email("ghost@example.com"))


class TestUpdate:
    async def test_changes_password(self, repo, make_user):
        user = make_user()
        await repo.add(user)
        new_hash = HashedPassword("$2b$12$newhash")
        await repo.update(user.id, new_password=new_hash)
        assert user.hashed_password == new_hash

    async def test_noop_when_password_is_none(self, repo, make_user):
        user = make_user()
        await repo.add(user)
        original = user.hashed_password
        await repo.update(user.id, new_password=None)
        assert user.hashed_password == original

    async def test_missing_raises(self, repo):
        with pytest.raises(UserNotFoundError):
            await repo.update(
                UserId.generate(), new_password=HashedPassword("$2b$12$x")
            )


class TestDelete:
    async def test_removes_user_and_frees_email(self, repo, make_user):
        user = make_user(email="user@example.com")
        await repo.add(user)

        await repo.delete(user.id)

        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(user.id)
        assert await repo.exists_by_email(Email("user@example.com")) is False

    async def test_missing_raises(self, repo):
        with pytest.raises(UserNotFoundError):
            await repo.delete(UserId.generate())


class TestExists:
    async def test_exists_by_id_true(self, repo, make_user):
        user = make_user()
        await repo.add(user)
        assert await repo.exists_by_id(user.id) is True

    async def test_exists_by_id_false(self, repo):
        assert await repo.exists_by_id(UserId.generate()) is False

    async def test_exists_by_email_true(self, repo, make_user):
        await repo.add(make_user(email="user@example.com"))
        assert await repo.exists_by_email(Email("user@example.com")) is True

    async def test_exists_by_email_false(self, repo):
        assert await repo.exists_by_email(Email("ghost@example.com")) is False