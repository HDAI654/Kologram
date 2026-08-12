import logging
from types import TracebackType
from sqlalchemy.exc import OperationalError, SQLAlchemyError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.ports.unit_of_work import UnitOfWork
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)

logger = logging.getLogger(__name__)


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self.users: SQLAlchemyUserRepository

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SQLAlchemyUserRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        await self._run("commit", self._session.commit)

    async def rollback(self) -> None:
        await self._run("rollback", self._session.rollback)

    async def _run(self, name: str, coro):
        try:
            return await coro()
        except OperationalError as exc:
            raise DatabaseConnectionError(str(exc)) from exc
        except TimeoutError as exc:
            raise DatabaseTimeoutError(str(exc)) from exc
        except SQLAlchemyError as exc:
            raise DatabaseOperationError(str(exc)) from exc
