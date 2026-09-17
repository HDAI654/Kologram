import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.domain.value_objects.email import Email
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheTimeoutError,
)
from src.infrastructure.cache.redis_verification_token_repository import (
    RedisVerificationTokenRepository,
)


@pytest.fixture
def repo(redis_client) -> RedisVerificationTokenRepository:
    return RedisVerificationTokenRepository(redis_client)


class TestAdd:
    async def test_uses_setex_with_ttl_and_email(self, repo, redis_client):
        token = VerificationToken.generate()
        await repo.add(
            token=token,
            email=Email("user@example.com"),
            token_type="verifyemail",
            ttl_seconds=600,
        )
        args = redis_client.setex.call_args.args
        assert "verifyemail" in args[0]
        assert token.value in args[0]
        assert args[1] == 600
        assert args[2] == "user@example.com"

    async def test_connection_error_translated(self, repo, redis_client):
        redis_client.setex.side_effect = RedisConnectionError("down")
        with pytest.raises(CacheConnectionError):
            await repo.add(
                token=VerificationToken.generate(),
                email=Email("user@example.com"),
                token_type="verifyemail",
                ttl_seconds=600,
            )


class TestGet:
    async def test_returns_email_when_present(self, repo, redis_client):
        redis_client.get.return_value = b"user@example.com"
        result = await repo.get(VerificationToken.generate(), "verifyemail")
        assert result is not None
        assert result.value == "user@example.com"

    async def test_returns_none_when_missing(self, repo, redis_client):
        redis_client.get.return_value = None
        assert await repo.get(VerificationToken.generate(), "verifyemail") is None

    async def test_handles_str_value(self, repo, redis_client):
        redis_client.get.return_value = "user@example.com"
        result = await repo.get(VerificationToken.generate(), "verifyemail")
        assert result is not None
        assert result.value == "user@example.com"

    async def test_connection_error_translated(self, repo, redis_client):
        redis_client.get.side_effect = RedisConnectionError("down")
        with pytest.raises(CacheConnectionError):
            await repo.get(VerificationToken.generate(), "verifyemail")

    async def test_timeout_error_translated(self, repo, redis_client):
        redis_client.get.side_effect = RedisTimeoutError("slow")
        with pytest.raises(CacheTimeoutError):
            await repo.get(VerificationToken.generate(), "verifyemail")

    async def test_generic_error_translated(self, repo, redis_client):
        redis_client.get.side_effect = RedisError("bad")
        with pytest.raises(CacheOperationError):
            await repo.get(VerificationToken.generate(), "verifyemail")


class TestDelete:
    async def test_calls_del_with_key(self, repo, redis_client):
        token = VerificationToken.generate()
        await repo.delete(token, "verifyemail")
        args = redis_client.delete.call_args.args
        assert "verifyemail" in args[0]
        assert token.value in args[0]

    async def test_connection_error_translated(self, repo, redis_client):
        redis_client.delete.side_effect = RedisConnectionError("down")
        with pytest.raises(CacheConnectionError):
            await repo.delete(VerificationToken.generate(), "verifyemail")