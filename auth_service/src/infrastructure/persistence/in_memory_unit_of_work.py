from types import TracebackType
from src.domain.ports.unit_of_work import UnitOfWork
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(self, users: InMemoryUserRepository | None = None) -> None:
        self.users = users or InMemoryUserRepository()
        self._committed = False

    async def __aenter__(self) -> "InMemoryUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self._committed = True

    async def rollback(self) -> None:
        self._committed = False
