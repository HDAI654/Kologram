"""SQLAlchemyListingRepository — full method coverage + error mapping."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError

from src.domain.entities.listing import Listing
from src.domain.value_objects.listing_id import ListingId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
    ListingNotFoundError,
)
from src.infrastructure.persistence.repositories.sqlalchemy_listing_repository import (
    SQLAlchemyListingRepository,
)

SELLER = "550e8400-e29b-41d4-a716-446655440000"
LISTING_ID = "550e8400-e29b-41d4-a716-446655440001"
CATEGORY_ID = "550e8400-e29b-41d4-a716-446655440002"


def _make_listing() -> Listing:
    return Listing.create(
        seller_id=SELLER,
        category_id=CATEGORY_ID,
        title="Mock Listing Title",
        description="d",
        price_amount="10",
        quantity=1,
        location="Berlin",
        id=LISTING_ID,
    )


def _session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    return session


class TestSQLAlchemyListingRepository:
    @pytest.mark.asyncio
    async def test_add_flushes(self) -> None:
        session = _session()
        repo = SQLAlchemyListingRepository(session)
        await repo.add(_make_listing())
        session.add.assert_called_once()
        session.flush.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(ListingNotFoundError):
            await repo.get_by_id(ListingId(LISTING_ID))

    @pytest.mark.asyncio
    async def test_update_not_found(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(ListingNotFoundError):
            await repo.update(_make_listing())

    @pytest.mark.asyncio
    async def test_delete_not_found(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(ListingNotFoundError):
            await repo.delete(ListingId(LISTING_ID))

    @pytest.mark.asyncio
    async def test_delete_success(self) -> None:
        session = _session()
        model = MagicMock()
        result = MagicMock()
        result.scalar_one_or_none.return_value = model
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        await repo.delete(ListingId(LISTING_ID))
        session.delete.assert_awaited()
        session.flush.assert_awaited()

    @pytest.mark.asyncio
    async def test_list_by_seller_empty(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        assert await repo.list_by_seller(UserId(SELLER)) == []

    @pytest.mark.asyncio
    async def test_search_empty(self) -> None:
        session = _session()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        session.execute = AsyncMock(return_value=result)
        repo = SQLAlchemyListingRepository(session)
        assert await repo.search(query="cam") == []

    @pytest.mark.asyncio
    async def test_integrity_error_maps_to_operation_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(
            side_effect=IntegrityError("stmt", {}, Exception("dup"))
        )
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(DatabaseOperationError):
            await repo.add(_make_listing())

    @pytest.mark.asyncio
    async def test_operational_error_maps_to_connection_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(
            side_effect=OperationalError("stmt", {}, Exception("down"))
        )
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(DatabaseConnectionError):
            await repo.add(_make_listing())

    @pytest.mark.asyncio
    async def test_timeout_maps_to_timeout_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(side_effect=TimeoutError("slow"))
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(DatabaseTimeoutError):
            await repo.add(_make_listing())

    @pytest.mark.asyncio
    async def test_sqlalchemy_error_maps_to_operation_error(self) -> None:
        session = _session()
        session.flush = AsyncMock(side_effect=SQLAlchemyError("boom"))
        repo = SQLAlchemyListingRepository(session)
        with pytest.raises(DatabaseOperationError):
            await repo.add(_make_listing())
