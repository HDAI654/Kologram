import pytest
import uuid
from unittest.mock import AsyncMock, Mock, MagicMock

from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker

from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.device import Device


@pytest.fixture
def mock_uow():
    """Mock UnitOfWork with async context manager support."""
    uow = AsyncMock(spec=UnitOfWork)
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.users = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_session_repository():
    repo = AsyncMock(spec=SessionRepository)
    repo.add = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.delete = AsyncMock()
    repo.delete_all_other_sessions = AsyncMock()
    repo.extend_session = AsyncMock()
    return repo


@pytest.fixture
def mock_token_decoder():
    decoder = Mock(spec=TokenDecoder)
    # Default payload – can be overridden in tests
    decoder.decode_and_validate.return_value = {
        "sub": "11111111-1111-1111-1111-111111111111",  # user id
        "sid": "22222222-2222-2222-2222-222222222222",  # session id
        "dev": "test-device",
        "token_type": "access",
        "exp": 9999999999,  # dummy expiry
    }
    return decoder


@pytest.fixture
def mock_token_encoder():
    encoder = Mock(spec=TokenEncoder)
    encoder.FIELD_TYPE_MAP = {}  # dummy
    encoder.create_access_token = Mock(return_value="access-token")
    encoder.create_refresh_token = Mock(return_value="refresh-token")
    return encoder


@pytest.fixture
def mock_password_hasher():
    hasher = Mock(spec=PasswordHasher)
    hasher.hash = Mock(return_value="hashed-password")
    hasher.verify = Mock(return_value=True)
    return hasher


@pytest.fixture
def mock_event_publisher():
    publisher = AsyncMock(spec=EventPublisher)
    publisher.publish = AsyncMock()
    return publisher


@pytest.fixture
def mock_verification_token_repository():
    repo = AsyncMock(spec=VerificationTokenRepository)
    repo.add = AsyncMock()
    repo.get = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_email_blocklist():
    checker = AsyncMock(spec=EmailBlocklistChecker)
    checker.is_blocked = AsyncMock(return_value=False)
    return checker