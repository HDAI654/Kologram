"""Unit tests for RedisSessionRepository (mocked client)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.entities.session import Session
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import SessionNotFoundError
from src.infrastructure.cache.redis_session_repository import RedisSessionRepository


def _repo() -> tuple[RedisSessionRepository, AsyncMock]:
    client = AsyncMock()
    pipeline = MagicMock()
    pipeline.hset = MagicMock(return_value=pipeline)
    pipeline.expire = MagicMock(return_value=pipeline)
    pipeline.sadd = MagicMock(return_value=pipeline)
    pipeline.delete = MagicMock(return_value=pipeline)
    pipeline.srem = MagicMock(return_value=pipeline)
    pipeline.execute = AsyncMock(return_value=[1, True, 1])
    client.pipeline = MagicMock(return_value=pipeline)
    return RedisSessionRepository(client), client


@pytest.mark.asyncio
async def test_add_session_uses_pipeline() -> None:
    repo, client = _repo()
    session = Session.create(
        user_id="11111111-1111-4111-8111-111111111111", device="web"
    )
    await repo.add(session)
    client.pipeline.assert_called()
    client.pipeline.return_value.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_by_id_missing() -> None:
    repo, client = _repo()
    client.hgetall = AsyncMock(return_value={})
    with pytest.raises(SessionNotFoundError):
        await repo.get_by_id(SessionId.generate())


@pytest.mark.asyncio
async def test_get_by_id_found() -> None:
    repo, client = _repo()
    uid = "11111111-1111-4111-8111-111111111111"
    sid = "22222222-2222-4222-8222-222222222222"
    client.hgetall = AsyncMock(
        return_value={
            b"id": sid.encode(),
            b"user_id": uid.encode(),
            b"device": b"web",
            b"created_at": b"2026-08-01",
        }
    )
    session = await repo.get_by_id(SessionId(sid))
    assert session.id.value == sid
    assert session.user_id.value == uid


@pytest.mark.asyncio
async def test_extend_missing_raises() -> None:
    repo, client = _repo()
    client.expire = AsyncMock(return_value=False)
    with pytest.raises(SessionNotFoundError):
        await repo.extend_session(SessionId.generate())
