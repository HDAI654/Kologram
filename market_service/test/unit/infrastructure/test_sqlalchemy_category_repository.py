"""SQLAlchemyCategoryRepository — full method coverage + error mapping."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.domain.entities.category import Category
from src.domain.value_objects.category_id import CategoryId
from src.domain.value_objects.category_name import CategoryName
from src.exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
)
from src.infrastructure.persistence.repositories.sqlalchemy_category_repository import (
    SQLAlchemyCategoryRepository,
)

MISSING = "550e8400-e29b-41d4-a716-446655440099"


def _session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


class TestSQLAlchemyCategoryRepository:
    @pytest.mark.asyncio
    async def test_add_flushes(self) -> None:
        session = _session()
        repo = SQLAlchemyCategoryRepository(session)
        await repo.add(Category.create(name="Books"))
        session.add.assert_called_once()
        session.flush.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(CategoryNotFoundError):
            await repo.get_by_id(CategoryId(MISSING))

    @pytest.mark.asyncio
    async def test_get_by_name_none(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyCategoryRepository(session)
        assert await repo.get_by_name(CategoryName("Missing Name")) is None

    @pytest.mark.asyncio
    async def test_update_not_found(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(CategoryNotFoundError):
            await repo.update(Category.create(name="Ghost Cat"))

    @pytest.mark.asyncio
    async def test_list_all_and_children_empty(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyCategoryRepository(session)
        assert await repo.list_all(active_only=True) == []
        assert await repo.list_children(CategoryId(MISSING)) == []

    @pytest.mark.asyncio
    async def test_integrity_duplicate_maps_to_already_exists(self) -> None:
        session = _session()
        session.flush = AsyncMock(
            side_effect=IntegrityError("stmt", {}, Exception("unique constraint"))
        )
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(CategoryAlreadyExistsError):
            await repo.add(Category.create(name="DupCat"))

    @pytest.mark.asyncio
    async def test_operational_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(
            side_effect=OperationalError("stmt", {}, Exception("down"))
        )
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(DatabaseConnectionError):
            await repo.add(Category.create(name="XX"))

    @pytest.mark.asyncio
    async def test_sqlalchemy_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(side_effect=SQLAlchemyError("boom"))
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(DatabaseOperationError):
            await repo.add(Category.create(name="YY"))

    @pytest.mark.asyncio
    async def test_timeout_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(side_effect=TimeoutError("slow"))
        repo = SQLAlchemyCategoryRepository(session)
        with pytest.raises(DatabaseTimeoutError):
            await repo.add(Category.create(name="ZZ"))
