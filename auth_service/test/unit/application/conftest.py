from unittest.mock import AsyncMock, MagicMock
import pytest
from src.domain.entities.user import User
from src.domain.value_objects.hashed_password import HashedPassword


@pytest.fixture
def sample_user() -> User:
    return User.create(email="trader@example.com", hashed_password="hashed-secret")


@pytest.fixture
def mock_uow() -> AsyncMock:
    uow = AsyncMock()
    uow.users = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    return uow


@pytest.fixture
def mock_sessions() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_encoder() -> MagicMock:
    enc = MagicMock()
    enc.FIELD_TYPE_MAP = {
        "sub": str,
        "sid": str,
        "dev": str,
        "type": str,
        "exp": (int, float),
    }
    enc.create_access_token = MagicMock(return_value="access.jwt")
    enc.create_refresh_token = MagicMock(return_value="refresh.jwt")
    return enc


@pytest.fixture
def mock_decoder() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_hasher() -> MagicMock:
    hasher = MagicMock()
    hasher.hash = MagicMock(return_value=HashedPassword("hashed-secret"))
    hasher.verify = MagicMock(return_value=True)
    return hasher


@pytest.fixture
def mock_events() -> AsyncMock:
    pub = AsyncMock()
    pub.publish = AsyncMock()
    return pub


@pytest.fixture
def mock_token_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_email_sender() -> AsyncMock:
    sender = AsyncMock()
    sender.send = AsyncMock()
    return sender


@pytest.fixture
def mock_blocklist() -> AsyncMock:
    checker = AsyncMock()
    checker.is_blocked = AsyncMock(return_value=False)
    return checker
