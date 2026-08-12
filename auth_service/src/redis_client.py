from redis.asyncio import Redis
from src.conf import Config


def create_redis_client(url: str | None = None) -> Redis:
    """Create an async Redis client from configuration."""
    return Redis.from_url(
        url or Config.REDIS_URL,
        encoding="utf-8",
        decode_responses=False,
    )
