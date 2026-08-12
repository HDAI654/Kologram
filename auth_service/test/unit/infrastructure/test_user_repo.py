import pytest
import pytest_asyncio

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.exceptions import UserAlreadyExistsError, UserNotFoundError
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


@pytest.mark.asyncio
async def test_add_get_by_email(session_factory) -> None:
    async with session_factory() as session:
        repo = SQLAlchemyUserRepository(session)
        user = User.create(email="u@example.com", hashed_password="hash")
        await repo.add(user)
        await session.commit()
        loaded = await repo.get_by_email(Email("u@example.com"))
        assert loaded.id == user.id


@pytest.mark.asyncio
async def test_duplicate_email_raises(session_factory) -> None:
    async with session_factory() as session:
        repo = SQLAlchemyUserRepository(session)
        await repo.add(User.create(email="dup@example.com", hashed_password="h1"))
        await session.commit()
        with pytest.raises(UserAlreadyExistsError):
            await repo.add(User.create(email="dup@example.com", hashed_password="h2"))


@pytest.mark.asyncio
async def test_update_password_and_delete(session_factory) -> None:
    async with session_factory() as session:
        repo = SQLAlchemyUserRepository(session)
        user = User.create(email="z@example.com", hashed_password="old")
        await repo.add(user)
        await session.commit()
        await repo.update(user.id, new_password=HashedPassword("new"))
        await session.commit()
        loaded = await repo.get_by_id(user.id)
        assert loaded.hashed_password.value == "new"
        await repo.delete(user.id)
        await session.commit()
        with pytest.raises(UserNotFoundError):
            await repo.get_by_id(user.id)
