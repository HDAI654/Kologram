import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.domain.entities.session import Session
from src.domain.entities.user import User

# ---------------------------------------------------------------------------
# SQLAlchemy session helpers
# ---------------------------------------------------------------------------


def _session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


def scalar_one_or_none(value: Any) -> MagicMock:
    result = MagicMock()
    result.scalar_one_or_none.return_value = value
    return result


def scalars_all(values: list[Any]) -> MagicMock:
    scalars = MagicMock()
    scalars.all.return_value = values
    result = MagicMock()
    result.scalars.return_value = scalars
    return result


@pytest.fixture
def session() -> AsyncMock:
    return _session()


# ---------------------------------------------------------------------------
# redis.asyncio fake
# ---------------------------------------------------------------------------


def _pipeline() -> MagicMock:
    """A redis asyncio Pipeline: command methods are sync, execute() is async."""
    pipe = MagicMock()
    pipe.hset = MagicMock()
    pipe.expire = MagicMock()
    pipe.sadd = MagicMock()
    pipe.delete = MagicMock()
    pipe.srem = MagicMock()
    pipe.execute = AsyncMock(return_value=[1, 1, 1])
    return pipe


@pytest.fixture
def redis_client() -> AsyncMock:
    """Mocked redis.asyncio.Redis client suitable for both repositories."""
    client = AsyncMock()
    client.pipeline = MagicMock(return_value=_pipeline())
    return client


@pytest.fixture
def redis_pipeline() -> MagicMock:
    """Same pipeline object the client fixture will hand out, for assertions."""
    pipe = _pipeline()
    return pipe


# ---------------------------------------------------------------------------
# aio_pika fake
# ---------------------------------------------------------------------------


class _FakeExchange:
    def __init__(self) -> None:
        self.published: list[tuple[Any, str]] = []
        self.publish = AsyncMock(side_effect=self._record)

    async def _record(self, message: Any, routing_key: str) -> None:
        self.published.append((message, routing_key))


class _FakeChannel:
    def __init__(self, exchange: _FakeExchange) -> None:
        self._exchange = exchange
        self.declare_exchange = AsyncMock(return_value=exchange)


class _FakeConnection:
    def __init__(self, channel: _FakeChannel) -> None:
        self._channel = channel
        self.is_closed = False
        self.channel = AsyncMock(return_value=channel)
        self.close = AsyncMock(side_effect=self._mark_closed)

    async def _mark_closed(self) -> None:
        self.is_closed = True


class FakeAioPika:
    class ExchangeType:
        def __init__(self, value: str) -> None:
            self.value = value

    def __init__(self) -> None:
        self.exchange = _FakeExchange()
        self.channel = _FakeChannel(self.exchange)
        self.connection = _FakeConnection(self.channel)
        self.connect_robust = AsyncMock(return_value=self.connection)
        self.Message = self._make_message

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
# Domain fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def make_user():
    def _make(
        *,
        email: str = "user@example.com",
        hashed_password: str = "$2b$12$defaulthashvalue",
        status: str = "ACTIVE",
        user_id: str | None = None,
    ) -> User:
        return User.create(
            email=email,
            hashed_password=hashed_password,
            id=user_id,
            status=status,
        )

    return _make


@pytest.fixture
def make_session():
    def _make(
        *,
        user_id: str,
        device: str = "iPhone 15",
        session_id: str | None = None,
    ) -> Session:
        return Session.create(user_id=user_id, device=device, id=session_id)

    return _make
