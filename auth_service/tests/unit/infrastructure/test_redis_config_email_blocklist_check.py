from unittest.mock import AsyncMock
import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError
from src.domain.value_objects.email import Email
from src.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheTimeoutError,
)
from src.infrastructure.cache.redis_email_blocklist_checker import (
    RedisEmailBlocklistChecker,
)

KEY = "blocked:emails"


@pytest.fixture
def checker(redis_client) -> RedisEmailBlocklistChecker:
    return RedisEmailBlocklistChecker(redis_client, key=KEY)


class TestRedisEmailBlocklistChecker:
    async def test_returns_true_when_member(self, checker, redis_client):
        redis_client.sismember = AsyncMock(return_value=1)
        assert await checker.is_blocked(Email("spam@example.com")) is True
        redis_client.sismember.assert_awaited_once_with(KEY, "spam@example.com")

    async def test_returns_false_when_not_member(self, checker, redis_client):
        redis_client.sismember = AsyncMock(return_value=0)
        assert await checker.is_blocked(Email("user@example.com")) is False

    async def test_email_is_normalized_before_lookup(self, checker, redis_client):
        redis_client.sismember = AsyncMock(return_value=0)
        await checker.is_blocked(Email("User@Example.COM"))
        redis_client.sismember.assert_awaited_once_with(KEY, "user@example.com")

    async def test_connection_error_translated(self, checker, redis_client):
        redis_client.sismember = AsyncMock(side_effect=RedisConnectionError("down"))
        with pytest.raises(CacheConnectionError):
            await checker.is_blocked(Email("user@example.com"))

    async def test_timeout_error_translated(self, checker, redis_client):
        redis_client.sismember = AsyncMock(side_effect=RedisTimeoutError("slow"))
        with pytest.raises(CacheTimeoutError):
            await checker.is_blocked(Email("user@example.com"))

    async def test_generic_redis_error_translated(self, checker, redis_client):
        redis_client.sismember = AsyncMock(side_effect=RedisError("bad"))
        with pytest.raises(CacheOperationError):
            await checker.is_blocked(Email("user@example.com"))

    async def test_translation_preserves_cause(self, checker, redis_client):
        underlying = RedisConnectionError("down")
        redis_client.sismember = AsyncMock(side_effect=underlying)
        with pytest.raises(CacheConnectionError) as exc_info:
            await checker.is_blocked(Email("user@example.com"))
        assert exc_info.value.__cause__ is underlying
