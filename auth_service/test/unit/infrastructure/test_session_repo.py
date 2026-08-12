import pytest
import pytest_asyncio

from src.domain.entities.session import Session
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import SessionNotFoundError
from src.infrastructure.cache.in_memory_session_repository import (
    InMemorySessionRepository,
)


@pytest_asyncio.fixture
async def repo() -> InMemorySessionRepository:
    return InMemorySessionRepository()


@pytest.mark.asyncio
async def test_add_and_get(repo: InMemorySessionRepository) -> None:
    uid = UserId.generate()
    session = Session.create(user_id=uid.value, device="web")
    await repo.add(session)
    loaded = await repo.get_by_id(session.id)
    assert loaded.id == session.id


@pytest.mark.asyncio
async def test_get_missing_raises(repo: InMemorySessionRepository) -> None:
    with pytest.raises(SessionNotFoundError):
        await repo.get_by_id(SessionId.generate())


@pytest.mark.asyncio
async def test_delete_and_delete_others(repo: InMemorySessionRepository) -> None:
    uid = UserId.generate()
    s1 = Session.create(user_id=uid.value, device="web")
    s2 = Session.create(user_id=uid.value, device="ios")
    await repo.add(s1)
    await repo.add(s2)
    await repo.delete_all_other_sessions(current_session_id=s1.id, user_id=uid)
    await repo.get_by_id(s1.id)
    with pytest.raises(SessionNotFoundError):
        await repo.get_by_id(s2.id)
