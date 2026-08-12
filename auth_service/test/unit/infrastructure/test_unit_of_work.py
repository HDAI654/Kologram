import pytest

from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_commit_persists_user(session_factory) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    async with uow:
        user = User.create(email="uow@example.com", hashed_password="h")
        await uow.users.add(user)
        await uow.commit()

    uow2 = SQLAlchemyUnitOfWork(session_factory)
    async with uow2:
        loaded = await uow2.users.get_by_email(Email("uow@example.com"))
        assert loaded.email.value == "uow@example.com"


@pytest.mark.asyncio
async def test_rollback_discards_user(session_factory) -> None:
    uow = SQLAlchemyUnitOfWork(session_factory)
    async with uow:
        await uow.users.add(User.create(email="rb@example.com", hashed_password="h"))
        await uow.rollback()

    uow2 = SQLAlchemyUnitOfWork(session_factory)
    async with uow2:
        assert await uow2.users.exists_by_email(Email("rb@example.com")) is False
