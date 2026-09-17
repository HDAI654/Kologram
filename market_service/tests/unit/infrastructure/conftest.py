from __future__ import annotations
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# ---------------------------------------------------------------------------
# SQLAlchemy session / result helpers
# ---------------------------------------------------------------------------


def make_session() -> AsyncMock:
    """Return an AsyncSession-shaped double suitable for repository tests."""
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


def make_scalar_one_or_none_result(value: Any) -> MagicMock:
    """Build an execute() result whose scalar_one_or_none() returns ``value``."""
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def make_scalars_all_result(values: list[Any]) -> MagicMock:
    """Build an execute() result whose .scalars().all() returns ``values``."""
    scalars = MagicMock()
    scalars.all.return_value = values
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


@pytest.fixture
def session() -> AsyncMock:
    return make_session()


# ---------------------------------------------------------------------------
# aio_pika fake
# ---------------------------------------------------------------------------


class FakeExchange:
    def __init__(self) -> None:
        self.published: list[tuple[Any, str]] = []
        self.publish = AsyncMock(side_effect=self._record)

    async def _record(self, message: Any, routing_key: str) -> None:
        self.published.append((message, routing_key))


class FakeChannel:
    def __init__(self, exchange: FakeExchange) -> None:
        self._exchange = exchange
        self.declare_exchange = AsyncMock(return_value=exchange)


class FakeConnection:
    def __init__(self, channel: FakeChannel) -> None:
        self._channel = channel
        self.is_closed = False
        self.channel = AsyncMock(return_value=channel)
        self.close = AsyncMock(side_effect=self._mark_closed)

    async def _mark_closed(self) -> None:
        self.is_closed = True


class FakeAioPika:
    """Minimal stand-in for the ``aio_pika`` module used by the publisher."""

    class DeliveryMode:
        PERSISTENT = 2
        NON_PERSISTENT = 1

    def __init__(self) -> None:
        self.exchange = FakeExchange()
        self.channel = FakeChannel(self.exchange)
        self.connection = FakeConnection(self.channel)
        self.Message = self._make_message
        self.ExchangeType = lambda value: value
        self.connect_robust = AsyncMock(return_value=self.connection)

    @staticmethod
    def _make_message(**kwargs: Any) -> MagicMock:
        msg = MagicMock()
        for key, value in kwargs.items():
            setattr(msg, key, value)
        return msg


@pytest.fixture
def fake_aio_pika(monkeypatch: pytest.MonkeyPatch) -> FakeAioPika:
    fake = FakeAioPika()
    monkeypatch.setitem(sys.modules, "aio_pika", fake)
    return fake


# ---------------------------------------------------------------------------
# Domain fixtures (real domain objects, no infrastructure)
# ---------------------------------------------------------------------------


@pytest.fixture
def make_category():
    from src.domain.entities.category import Category

    def _make(
        *,
        name: str = "Electronics",
        parent_id: str | None = None,
        is_active: bool = True,
    ) -> Category:
        return Category.create(name=name, parent_id=parent_id, is_active=is_active)

    return _make


@pytest.fixture
def make_listing():
    from src.domain.entities.listing import Listing
    from src.domain.value_objects.category_id import CategoryId
    from src.domain.value_objects.user_id import UserId

    def _make(
        *,
        seller_id: str | None = None,
        category_id: str | None = None,
        status: str = "DRAFT",
        title: str = "Test Listing",
        description: str = "A description",
        price_amount: str = "100.00",
        quantity: int = 5,
        location: str = "New York",
        currency: str = "USD",
    ) -> Listing:
        return Listing.create(
            seller_id=seller_id or UserId.generate().value,
            category_id=category_id or CategoryId.generate().value,
            title=title,
            description=description,
            price_amount=price_amount,
            quantity=quantity,
            location=location,
            currency=currency,
            status=status,
        )

    return _make
