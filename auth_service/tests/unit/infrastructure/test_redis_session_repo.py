from datetime import date

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.conf import Config
from src.domain.entities.session import Session
from src.domain.value_objects.date import Date
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheTimeoutError,
    SessionNotFoundError,
)
from src.infrastructure.cache.redis_session_repository import (
    RedisSessionRepository,
)


@pytest.fixture
def repo(redis_client) -> RedisSessionRepository:
    return RedisSessionRepository(redis_client)


class TestAdd:
    async def test_queues_hash_expire_and_sadd(self, repo, redis_client, make_session):
        session = make_session(user_id=UserId.generate().value)
        pipe = redis_client.pipeline.return_value

        await repo.add(session)

        pipe.hset.assert_called_once()
        pipe.expire.assert_called_once()
        pipe.sadd.assert_called_once()
        pipe.execute.assert_awaited_once()

    async def test_hash_mapping_contains_serialized_fields(
        self, repo, redis_client, make_session
    ):
        session = make_session(user_id=UserId.generate().value)
        pipe = redis_client.pipeline.return_value

        await repo.add(session)

        mapping = pipe.hset.call_args.kwargs["mapping"]
        assert mapping["id"] == session.id.value
        assert mapping["user_id"] == session.user_id.value
        assert mapping["device"] == session.device.value
        assert mapping["created_at"] == session.created_at.value.isoformat()

    async def test_uses_refresh_ttl(self, repo, redis_client, make_session):
        session = make_session(user_id=UserId.generate().value)
        pipe = redis_client.pipeline.return_value

        await repo.add(session)

        ttl_arg = pipe.expire.call_args.args[1]
        assert ttl_arg == Config.REFRESH_TOKEN_EXPIRE_MINUTES * 60

    async def test_connection_error_translated(self, repo, redis_client, make_session):
        pipe = redis_client.pipeline.return_value
        pipe.execute = __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock(
            side_effect=RedisConnectionError("down")
        )
        with pytest.raises(CacheConnectionError):
            await repo.add(make_session(user_id=UserId.generate().value))


class TestGetById:
    async def test_returns_deserialized_session(self, repo, redis_client):
        raw = {
            b"id": b"1a2b3c4d-1111-4111-8111-111111111111",
            b"user_id": b"2a2b3c4d-2222-4222-8222-222222222222",
            b"device": b"iPhone",
            b"created_at": b"2024-01-15",
        }
        redis_client.hgetall.return_value = raw

        result = await repo.get_by_id(SessionId("1a2b3c4d-1111-4111-8111-111111111111"))

        assert isinstance(result, Session)
        assert result.device.value == "iPhone"
        assert result.created_at.value == date(2024, 1, 15)

    async def test_missing_raises(self, repo, redis_client):
        redis_client.hgetall.return_value = {}
        with pytest.raises(SessionNotFoundError):
            await repo.get_by_id(SessionId.generate())

    async def test_connection_error_translated(self, repo, redis_client):
        redis_client.hgetall.side_effect = RedisConnectionError("down")
        with pytest.raises(CacheConnectionError):
            await repo.get_by_id(SessionId.generate())

    async def test_timeout_error_translated(self, repo, redis_client):
        redis_client.hgetall.side_effect = RedisTimeoutError("slow")
        with pytest.raises(CacheTimeoutError):
            await repo.get_by_id(SessionId.generate())

    async def test_generic_redis_error_translated(self, repo, redis_client):
        redis_client.hgetall.side_effect = RedisError("bad")
        with pytest.raises(CacheOperationError):
            await repo.get_by_id(SessionId.generate())


class TestDelete:
    async def test_raises_when_nothing_deleted(self, repo, redis_client):
        pipe = redis_client.pipeline.return_value
        pipe.execute = __import__("unittest.mock", fromlist=["AsyncMock"]).AsyncMock(
            return_value=[0, 0]
        )
        with pytest.raises(SessionNotFoundError):
            await repo.delete(SessionId.generate(), UserId.generate())


class TestDeleteAllOtherSessions:
    async def test_noop_when_no_other_sessions(self, repo, redis_client):
        current = SessionId.generate()
        redis_client.smembers.return_value = [current.value.encode()]

        await repo.delete_all_other_sessions(current, UserId.generate())

        redis_client.pipeline.assert_not_called()

    async def test_deletes_others_and_updates_set(self, repo, redis_client):
        current = SessionId.generate()
        other_a = SessionId.generate().value
        other_b = SessionId.generate().value
        redis_client.smembers.return_value = [
            current.value.encode(),
            other_a.encode(),
            other_b.encode(),
        ]
        pipe = redis_client.pipeline.return_value

        await repo.delete_all_other_sessions(current, UserId.generate())

        pipe.delete.assert_called_once()
        pipe.srem.assert_called_once()
        pipe.execute.assert_awaited_once()


class TestExtendSession:
    async def test_extends_when_key_exists(self, repo, redis_client):
        redis_client.expire.return_value = 1
        await repo.extend_session(SessionId.generate())
        redis_client.expire.assert_awaited_once()

    async def test_raises_when_key_missing(self, repo, redis_client):
        redis_client.expire.return_value = 0
        with pytest.raises(SessionNotFoundError):
            await repo.extend_session(SessionId.generate())

    async def test_connection_error_translated(self, repo, redis_client):
        redis_client.expire.side_effect = RedisConnectionError("down")
        with pytest.raises(CacheConnectionError):
            await repo.extend_session(SessionId.generate())
