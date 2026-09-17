from src.infrastructure.persistence.in_memory_unit_of_work import (
    InMemoryUnitOfWork,
)
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


class TestInMemoryUnitOfWork:
    async def test_creates_default_user_repo(self):
        uow = InMemoryUnitOfWork()
        assert isinstance(uow.users, InMemoryUserRepository)

    async def test_accepts_shared_user_repo(self):
        repo = InMemoryUserRepository()
        uow = InMemoryUnitOfWork(users=repo)
        assert uow.users is repo

    async def test_aenter_returns_self(self):
        uow = InMemoryUnitOfWork()
        async with uow as active:
            assert active is uow

    async def test_commit_sets_flag(self):
        uow = InMemoryUnitOfWork()
        await uow.commit()
        assert uow._committed is True

    async def test_rollback_clears_flag(self):
        uow = InMemoryUnitOfWork()
        await uow.commit()
        await uow.rollback()
        assert uow._committed is False

    async def test_aexit_is_noop(self):
        uow = InMemoryUnitOfWork()
        await uow.__aexit__(None, None, None)
