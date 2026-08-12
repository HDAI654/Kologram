import logging
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError
from src.conf import Config
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.domain.value_objects.email import Email
from src.domain.value_objects.email_verification_token import EmailVerificationToken
from src.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheTimeoutError,
)

logger = logging.getLogger(__name__)


class RedisVerificationTokenRepository(VerificationTokenRepository):
    """Stores verify-email and reset-password tokens with TTL in Redis."""

    def __init__(self, client: Redis) -> None:
        self._client = client
        self._prefix = Config.VERIFICATION_TOKEN_KEY_PREFIX

    async def add(
        self,
        token: EmailVerificationToken,
        email: Email,
        token_type: str,
        ttl_seconds: int,
    ) -> None:
        key = self._key(token, token_type)
        await self._execute_redis_operation(
            "add_token",
            self._client.setex,
            key,
            ttl_seconds,
            email.value,
        )

    async def get(
        self,
        token: EmailVerificationToken,
        token_type: str,
    ) -> Email | None:
        key = self._key(token, token_type)
        value = await self._execute_redis_operation("get_token", self._client.get, key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode()
        return Email(value)

    async def delete(
        self,
        token: EmailVerificationToken,
        token_type: str,
    ) -> None:
        key = self._key(token, token_type)
        await self._execute_redis_operation("delete_token", self._client.delete, key)

    def _key(self, token: EmailVerificationToken, token_type: str) -> str:
        return f"{self._prefix}{token_type}:{token.value}"

    async def _execute_redis_operation(self, operation: str, coro, *args, **kwargs):
        """Generic wrapper for Redis operations with error handling."""
        try:
            return await coro(*args, **kwargs)
        except RedisConnectionError as e:
            logger.exception("Failed to connect to Redis during %s", operation)
            raise CacheConnectionError(f"Failed to connect to cache: {e}") from e
        except RedisTimeoutError as e:
            logger.exception("Redis timeout during %s", operation)
            raise CacheTimeoutError(f"Cache operation timed out: {e}") from e
        except RedisError as e:
            logger.exception("Redis error during %s", operation)
            raise CacheOperationError(f"Cache operation failed: {e}") from e
