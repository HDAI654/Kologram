import logging
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError
from src.conf import Config
from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.value_objects.email import Email
from src.exceptions import (
    CacheConnectionError,
    CacheOperationError,
    CacheTimeoutError,
)

logger = logging.getLogger(__name__)


class RedisEmailBlocklistChecker(EmailBlocklistChecker):
    """Membership check against Redis set at BLOCKED_EMAILS_REDIS_KEY."""

    def __init__(self, client: Redis, key: str | None = None) -> None:
        self._client = client
        self._key = key or Config.BLOCKED_EMAILS_REDIS_KEY

    async def is_blocked(self, email: Email) -> bool:
        try:
            return bool(await self._client.sismember(self._key, email.value.lower()))
        except RedisConnectionError as e:
            logger.exception("Failed to connect to Redis during is_blocked")
            raise CacheConnectionError(f"Failed to connect to cache: {e}") from e
        except RedisTimeoutError as e:
            logger.exception("Redis timeout during is_blocked")
            raise CacheTimeoutError(f"Cache operation timed out: {e}") from e
        except RedisError as e:
            logger.exception("Redis error during is_blocked")
            raise CacheOperationError(f"Cache operation failed: {e}") from e
