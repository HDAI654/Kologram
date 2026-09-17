import pytest

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.mark.asyncio
async def test_add_get_delete() -> None:
    repo = InMemoryUserRepository()
    user = User.create(email="a@b.com", hashed_password="h")
    await repo.add(user)
    loaded = await repo.get_by_email(Email("a@b.com"))
    assert loaded.id == user.id
    await repo.update(user.id, new_password=HashedPassword("new"))
    loaded = await repo.get_by_id(user.id)
    assert loaded.hashed_password.value == "new"
    await repo.delete(user.id)
    with pytest.raises(UserNotFoundError):
        await repo.get_by_id(user.id)


@pytest.mark.asyncio
async def test_duplicate_email() -> None:
    repo = InMemoryUserRepository()
    await repo.add(User.create(email="a@b.com", hashed_password="h"))
    with pytest.raises(UserAlreadyExistsError):
        await repo.add(User.create(email="a@b.com", hashed_password="h2"))
