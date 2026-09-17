import uuid
import pytest
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import SessionNotFoundError
from src.infrastructure.cache.in_memory_session_repository import (
    InMemorySessionRepository,
)


@pytest.fixture
def repo() -> InMemorySessionRepository:
    return InMemorySessionRepository()


class TestAddAndGet:
    async def test_add_then_get(self, repo, make_session):
        session = make_session(user_id=UserId.generate().value)
        await repo.add(session)
        assert await repo.get_by_id(session.id) is session

    async def test_get_missing_raises(self, repo):
        with pytest.raises(SessionNotFoundError):
            await repo.get_by_id(SessionId.generate())


class TestDelete:
    async def test_delete_removes_session(self, repo, make_session):
        session = make_session(user_id=UserId.generate().value)
        await repo.add(session)

        await repo.delete(session.id, session.user_id)

        with pytest.raises(SessionNotFoundError):
            await repo.get_by_id(session.id)

    async def test_delete_missing_is_idempotent(self, repo):
        await repo.delete(SessionId.generate(), UserId.generate())


class TestDeleteAllOtherSessions:
    async def test_keeps_only_current(self, repo, make_session):
        user_id = UserId.generate().value
        keep = make_session(user_id=user_id)
        drop_a = make_session(user_id=user_id)
        drop_b = make_session(user_id=user_id)
        for s in (keep, drop_a, drop_b):
            await repo.add(s)

        await repo.delete_all_other_sessions(keep.id, UserId(user_id))

        assert await repo.get_by_id(keep.id) is keep
        for dropped in (drop_a, drop_b):
            with pytest.raises(SessionNotFoundError):
                await repo.get_by_id(dropped.id)

    async def test_does_not_touch_other_users(self, repo, make_session):
        mine = make_session(user_id=UserId.generate().value)
        other = make_session(user_id=UserId.generate().value)
        await repo.add(mine)
        await repo.add(other)

        await repo.delete_all_other_sessions(mine.id, mine.user_id)

        assert await repo.get_by_id(other.id) is other


class TestExtendSession:
    async def test_extend_missing_raises(self, repo):
        with pytest.raises(SessionNotFoundError):
            await repo.extend_session(SessionId.generate())

    async def test_extend_keeps_session(self, repo, make_session):
        session = make_session(user_id=UserId.generate().value)
        await repo.add(session)

        await repo.extend_session(session.id)

        assert await repo.get_by_id(session.id) is session