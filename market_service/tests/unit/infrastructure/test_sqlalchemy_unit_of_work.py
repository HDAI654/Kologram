from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)
from src.infrastructure.persistence.repositories.sqlalchemy_listing_repository import (
    SQLAlchemyListingRepository,
)
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork


@pytest.fixture
def session_factory(session):
    return MagicMock(return_value=session)


class TestEnterExit:
    async def test_aenter_creates_session_and_repositories(
        self, session_factory, session
    ):
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow as active:
            assert active is uow
            assert isinstance(active.listings, SQLAlchemyListingRepository)
            assert isinstance(active.categories, SQLAlchemyCategoryRepository)
            assert active._session is session

        session_factory.assert_called_once()

    async def test_aexit_without_exception_closes_session_without_rollback(
        self, session_factory, session
    ):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            pass

        session.close.assert_awaited_once()
        session.rollback.assert_not_awaited()
        assert uow._session is None

    async def test_aexit_with_exception_rolls_back_and_closes(
        self, session_factory, session
    ):
        uow = SQLAlchemyUnitOfWork(session_factory)

        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")

        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()
        assert uow._session is None

    async def test_aexit_is_safe_when_session_missing(self, session_factory):
        uow = SQLAlchemyUnitOfWork(session_factory)
        # __aexit__ without a preceding __aenter__ must not raise.
        await uow.__aexit__(None, None, None)

    async def test_session_closed_even_if_rollback_fails(
        self, session_factory, session
    ):
        session.rollback.side_effect = RuntimeError("rollback failed")
        uow = SQLAlchemyUnitOfWork(session_factory)

        with pytest.raises(RuntimeError):
            async with uow:
                raise RuntimeError("boom")

        session.close.assert_awaited_once()


class TestCommit:
    async def test_commit_delegates_to_session(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            await uow.commit()

        session.commit.assert_awaited_once()

    async def test_commit_translates_operational_error_to_connection_error(
        self, session_factory, session
    ):
        session.commit.side_effect = OperationalError("stmt", {}, Exception("down"))
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            with pytest.raises(DatabaseConnectionError):
                await uow.commit()

    async def test_commit_translates_sqlalchemy_error_to_operation_error(
        self, session_factory, session
    ):
        session.commit.side_effect = SQLAlchemyError("bad")
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            with pytest.raises(DatabaseOperationError):
                await uow.commit()

    async def test_commit_translates_timeout_to_timeout_error(
        self, session_factory, session
    ):
        session.commit.side_effect = TimeoutError("slow")
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            with pytest.raises(DatabaseTimeoutError):
                await uow.commit()

    async def test_commit_preserves_cause(self, session_factory, session):
        underlying = OperationalError("stmt", {}, Exception("down"))
        session.commit.side_effect = underlying
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            with pytest.raises(DatabaseConnectionError) as exc_info:
                await uow.commit()

        assert exc_info.value.__cause__ is underlying


class TestRollback:
    async def test_rollback_delegates_to_session(self, session_factory, session):
        uow = SQLAlchemyUnitOfWork(session_factory)
        async with uow:
            await uow.rollback()

        session.rollback.assert_awaited_once()

    async def test_rollback_translates_operational_error(
        self, session_factory, session
    ):
        session.rollback.side_effect = OperationalError("stmt", {}, Exception("down"))
        uow = SQLAlchemyUnitOfWork(session_factory)

        async with uow:
            with pytest.raises(DatabaseConnectionError):
                await uow.rollback()
