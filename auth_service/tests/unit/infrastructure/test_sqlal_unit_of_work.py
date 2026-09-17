from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError, SQLAlchemyError, TimeoutError

from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


@pytest.fixture
def session_factory(session):
    return MagicMock(return_value=session)


class TestEnter:
    async def test_aenter_creates_session_and_user_repo(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow as active:
            assert active is uow
            assert isinstance(active.users, SQLAlchemyUserRepository)
            assert active._session is session
        session_factory.assert_called_once()


class TestExit:
    async def test_clean_exit_closes_session(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            pass
        session.close.assert_awaited_once()
        session.rollback.assert_not_awaited()
        assert uow._session is None

    async def test_exception_rolls_back_then_closes(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")
        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()

    async def test_close_still_runs_when_rollback_fails(self, session_factory, session):
        session.rollback.side_effect = RuntimeError("rollback failed")
        uow = SQLAlchemyUnitOfWork(session_factory)
        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")
        session.close.assert_awaited_once()

    async def test_exit_without_enter_is_noop(self, session_factory):
        uow = SQLAlchemyUnitOfWork(session_factory)
        await uow.__aexit__(None, None, None)


class TestCommit:
    async def test_delegates_to_session(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            await uow.commit()
        session.commit.assert_awaited_once()

    async def test_operational_error_becomes_connection_error(
        self, session_factory, session
    ):
        session.commit.side_effect = OperationalError("stmt", {}, Exception("down"))
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            with pytest.raises(DatabaseConnectionError):
                await uow.commit()

    async def test_sqlalchemy_error_becomes_operation_error(
        self, session_factory, session
    ):
        session.commit.side_effect = SQLAlchemyError("bad")
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            with pytest.raises(DatabaseOperationError):
                await uow.commit()

    async def test_timeout_becomes_timeout_error(self, session_factory, session):
        session.commit.side_effect = TimeoutError("slow")
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            with pytest.raises(DatabaseTimeoutError):
                await uow.commit()

    async def test_preserves_cause(self, session_factory, session):
        underlying = OperationalError("stmt", {}, Exception("down"))
        session.commit.side_effect = underlying
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            with pytest.raises(DatabaseConnectionError) as exc_info:
                await uow.commit()
        assert exc_info.value.__cause__ is underlying


class TestRollback:
    async def test_delegates_to_session(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            await uow.rollback()
        session.rollback.assert_awaited_once()

    async def test_operational_error_becomes_connection_error(
        self, session_factory, session
    ):
        session.rollback.side_effect = OperationalError("stmt", {}, Exception("down"))
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            with pytest.raises(DatabaseConnectionError):
                await uow.rollback()
