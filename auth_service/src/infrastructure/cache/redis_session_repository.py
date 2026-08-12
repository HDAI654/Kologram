import logging
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

from src.conf import Config
from src.domain.entities.session import Session
from src.domain.ports.session_repository import SessionRepository
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

logger = logging.getLogger(__name__)


class RedisSessionRepository(SessionRepository):
    """Stores sessions in Redis with TTL aligned to refresh-token lifetime."""

    def __init__(self, client: Redis) -> None:
        self._client = client
        self._ttl_seconds = Config.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        self._session_prefix = Config.SESSION_KEY_PREFIX
        self._user_sessions_prefix = Config.USER_SESSIONS_KEY_PREFIX

    async def add(self, session: Session) -> None:
        logger.info(
            "Adding session id=%s user_id=%s",
            session.id.value,
            session.user_id.value,
        )
        pipeline = self._client.pipeline()
        session_key = self._session_key(session.id)
        pipeline.hset(session_key, mapping=self._serialize(session))
        pipeline.expire(session_key, self._ttl_seconds)
        pipeline.sadd(self._user_sessions_key(session.user_id), session.id.value)
        await self._execute_redis_operation("add_session", pipeline.execute)
        logger.info("Session added id=%s", session.id.value)

    async def get_by_id(self, session_id: SessionId) -> Session:
        data = await self._execute_redis_operation(
            "get_by_id",
            self._client.hgetall,
            self._session_key(session_id),
        )
        if not data:
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )
        return self._deserialize(data)

    async def delete(self, session_id: SessionId, user_id: UserId) -> None:
        pipeline = self._client.pipeline()
        pipeline.delete(self._session_key(session_id))
        pipeline.srem(self._user_sessions_key(user_id), session_id.value)
        results = await self._execute_redis_operation(
            "delete_session", pipeline.execute
        )
        if results[0] == 0:
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )

    async def delete_all_other_sessions(
        self,
        current_session_id: SessionId,
        user_id: UserId,
    ) -> None:
        user_key = self._user_sessions_key(user_id)
        all_ids = await self._execute_redis_operation(
            "smembers", self._client.smembers, user_key
        )
        to_delete = [
            sid.decode() if isinstance(sid, bytes) else sid
            for sid in all_ids
            if (sid.decode() if isinstance(sid, bytes) else sid)
            != current_session_id.value
        ]
        if not to_delete:
            return
        pipeline = self._client.pipeline()
        pipeline.delete(*(self._session_key(SessionId(sid)) for sid in to_delete))
        pipeline.srem(user_key, *to_delete)
        await self._execute_redis_operation(
            "delete_all_other_sessions", pipeline.execute
        )

    async def extend_session(self, session_id: SessionId) -> None:
        result = await self._execute_redis_operation(
            "extend_session",
            self._client.expire,
            self._session_key(session_id),
            self._ttl_seconds,
        )
        if not result:
            raise SessionNotFoundError(
                f"Session with id {session_id.value!r} not found"
            )

    def _session_key(self, session_id: SessionId) -> str:
        return f"{self._session_prefix}{session_id.value}"

    def _user_sessions_key(self, user_id: UserId) -> str:
        return f"{self._user_sessions_prefix}{user_id.value}"

    @staticmethod
    def _serialize(session: Session) -> dict[str, str]:
        return {
            "id": session.id.value,
            "user_id": session.user_id.value,
            "device": session.device.value,
            "created_at": session.created_at.value.isoformat(),
        }

    @staticmethod
    def _deserialize(data: dict) -> Session:
        decoded = {
            (k.decode() if isinstance(k, bytes) else k): (
                v.decode() if isinstance(v, bytes) else v
            )
            for k, v in data.items()
        }
        return Session(
            id=SessionId(decoded["id"]),
            user_id=UserId(decoded["user_id"]),
            device=Device(decoded["device"]),
            created_at=Date(decoded["created_at"]),
        )

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
