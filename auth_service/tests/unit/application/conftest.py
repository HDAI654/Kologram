import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import pytest
from src.domain.entities.session import Session
from src.domain.entities.user import User
from src.domain.value_objects.device import Device
from src.domain.value_objects.email import Email
from src.domain.value_objects.hashed_password import HashedPassword
from src.domain.value_objects.password import Password
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import SessionNotFoundError, UserNotFoundError

# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------


class FakeUserRepository:
    def __init__(self) -> None:
        self._by_id: dict[str, User] = {}
        self._by_email: dict[str, str] = {}
        self.added: list[User] = []
        self.updated: list[tuple[UserId, HashedPassword]] = []
        self.deleted: list[UserId] = []

    async def get_by_id(self, user_id: UserId) -> User:
        user = self._by_id.get(user_id.value)
        if user is None:
            raise UserNotFoundError(f"User '{user_id.value}' not found")
        return user

    async def get_by_email(self, email: Email) -> User:
        uid = self._by_email.get(email.value)
        if uid is None:
            raise UserNotFoundError(f"User with email '{email.value}' not found")
        return self._by_id[uid]

    async def add(self, user: User) -> None:
        self._by_id[user.id.value] = user
        self._by_email[user.email.value] = user.id.value
        self.added.append(user)

    async def update(
        self, user_id: UserId, *, new_password: HashedPassword | None = None
    ) -> None:
        user = await self.get_by_id(user_id)
        if new_password is not None:
            user.change_password(new_password)
            self.updated.append((user_id, new_password))

    async def delete(self, user_id: UserId) -> None:
        user = await self.get_by_id(user_id)
        del self._by_id[user.id.value]
        self._by_email.pop(user.email.value, None)
        self.deleted.append(user_id)

    async def exists_by_id(self, user_id: UserId) -> bool:
        return user_id.value in self._by_id

    async def exists_by_email(self, email: Email) -> bool:
        return email.value in self._by_email


class FakeSessionRepository:
    def __init__(self) -> None:
        self._store: dict[str, Session] = {}
        self.added: list[Session] = []
        self.deleted: list[tuple[str, str]] = []
        self.delete_other_calls: list[tuple[str, str]] = []
        self.extended: list[str] = []

    async def add(self, session: Session) -> None:
        self._store[session.id.value] = session
        self.added.append(session)

    async def get_by_id(self, session_id: SessionId) -> Session:
        session = self._store.get(session_id.value)
        if session is None:
            raise SessionNotFoundError(f"Session '{session_id.value}' not found")
        return session

    async def delete(self, session_id: SessionId, user_id: UserId) -> None:
        if session_id.value not in self._store:
            raise SessionNotFoundError(f"Session '{session_id.value}' not found")
        del self._store[session_id.value]
        self.deleted.append((session_id.value, user_id.value))

    async def delete_all_other_sessions(
        self, current_session_id: SessionId, user_id: UserId
    ) -> None:
        self.delete_other_calls.append((current_session_id.value, user_id.value))
        for sid in [
            s.id.value
            for s in self._store.values()
            if s.user_id == user_id and s.id.value != current_session_id.value
        ]:
            del self._store[sid]

    async def extend_session(self, session_id: SessionId) -> None:
        await self.get_by_id(session_id)
        self.extended.append(session_id.value)


class FakeVerificationTokenRepository:
    def __init__(self) -> None:
        self._store: dict[tuple[str, str], Email] = {}
        self.added: list[dict[str, Any]] = []
        self.deleted: list[tuple[str, str]] = []

    async def add(
        self,
        token: VerificationToken,
        email: Email,
        token_type: str,
        ttl_seconds: int,
    ) -> None:
        self._store[(token_type, token.value)] = email
        self.added.append(
            {
                "token": token.value,
                "email": email.value,
                "token_type": token_type,
                "ttl_seconds": ttl_seconds,
            }
        )

    async def get(self, token: VerificationToken, token_type: str) -> Email | None:
        return self._store.get((token_type, token.value))

    async def delete(self, token: VerificationToken, token_type: str) -> None:
        self._store.pop((token_type, token.value), None)
        self.deleted.append((token_type, token.value))


# ---------------------------------------------------------------------------
# Unit of Work
# ---------------------------------------------------------------------------


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.users = FakeUserRepository()
        self.committed = False
        self.commit_count = 0
        self.rolled_back = False
        self.entered = False
        self.exited = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.exited = True
        if exc_type is not None:
            self.rolled_back = True

    async def commit(self) -> None:
        self.committed = True
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rolled_back = True


# ---------------------------------------------------------------------------
# Security / messaging / cache
# ---------------------------------------------------------------------------


class FakeTokenEncoder:
    FIELD_TYPE_MAP = {
        "sub": str,
        "sid": str,
        "dev": str,
        "type": str,
        "exp": (int, float),
    }

    def create_access_token(
        self, user_id: UserId, session_id: SessionId, device: Device
    ) -> str:
        return f"access::{user_id.value}::{session_id.value}::{device.value}"

    def create_refresh_token(
        self, user_id: UserId, session_id: SessionId, device: Device
    ) -> str:
        return f"refresh::{user_id.value}::{session_id.value}::{device.value}"


class FakeTokenDecoder:
    def __init__(self) -> None:
        self.payload: dict[str, Any] = {}
        self.exception: Exception | None = None
        self.calls: list[dict[str, Any]] = []

    def decode_and_validate(
        self,
        field_type_map: dict,
        token: str,
        expected_token_type: str | None = None,
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "field_type_map": field_type_map,
                "token": token,
                "expected_token_type": expected_token_type,
            }
        )
        if self.exception is not None:
            raise self.exception
        return self.payload


class FakePasswordHasher:
    def __init__(self) -> None:
        self.verify_result = True
        self.hash_calls: list[str] = []
        self.verify_calls: list[tuple[str, str]] = []

    def hash(self, password: Password) -> HashedPassword:
        self.hash_calls.append(password.value)
        return HashedPassword(f"hashed::{password.value}")

    def verify(self, plain: str, hashed: HashedPassword) -> bool:
        self.verify_calls.append((plain, hashed.value))
        return self.verify_result


class FakeEventPublisher:
    def __init__(self) -> None:
        self.published: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.published.append(event)


class FakeEmailBlocklistChecker:
    def __init__(self, blocked: set[str] | None = None) -> None:
        self._blocked = blocked or set()

    async def is_blocked(self, email: Email) -> bool:
        return email.value in self._blocked


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def uow() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def session_repo() -> FakeSessionRepository:
    return FakeSessionRepository()


@pytest.fixture
def token_repo() -> FakeVerificationTokenRepository:
    return FakeVerificationTokenRepository()


@pytest.fixture
def encoder() -> FakeTokenEncoder:
    return FakeTokenEncoder()


@pytest.fixture
def decoder() -> FakeTokenDecoder:
    return FakeTokenDecoder()


@pytest.fixture
def hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def events() -> FakeEventPublisher:
    return FakeEventPublisher()


@pytest.fixture
def blocklist() -> FakeEmailBlocklistChecker:
    return FakeEmailBlocklistChecker()


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


@pytest.fixture
def valid_payload():
    def _make(
        *,
        user_id: str | None = None,
        session_id: str | None = None,
        device: str = "iPhone 15",
        exp: float | None = None,
        token_type: str = "access",
    ) -> dict[str, Any]:
        return {
            "sub": user_id or UserId.generate().value,
            "sid": session_id or SessionId.generate().value,
            "dev": device,
            "type": token_type,
            "exp": (
                exp
                if exp is not None
                else (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
            ),
        }

    return _make


@pytest.fixture
def unknown_uuid() -> str:
    return str(uuid.uuid4())
