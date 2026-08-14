"""RS256 JWT token encoder."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.conf import Config
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId


class JwtTokenEncoder(TokenEncoder):
    FIELD_TYPE_MAP: dict[str, type] = {
        "sub": str,
        "sid": str,
        "dev": str,
        "type": str,
        "role": str,
        "exp": (int, float),
        "iat": (int, float),
    }

    def __init__(
        self,
        private_key: str | None = None,
        algorithm: str | None = None,
        access_ttl_minutes: int | None = None,
        refresh_ttl_minutes: int | None = None,
    ) -> None:
        self._private_key = private_key or Config.AUTH_TOKEN_PRIVATE_KEY
        self._algorithm = algorithm or Config.AUTH_TOKEN_ALGORITHM
        self._access_ttl = access_ttl_minutes or Config.ACCESS_TOKEN_EXPIRE_MINUTES
        self._refresh_ttl = refresh_ttl_minutes or Config.REFRESH_TOKEN_EXPIRE_MINUTES

    def create_access_token(
        self,
        user_id: UserId,
        session_id: SessionId,
        device: Device,
    ) -> str:
        return self._encode(user_id, session_id, device, "access", self._access_ttl)

    def create_refresh_token(
        self,
        user_id: UserId,
        session_id: SessionId,
        device: Device,
    ) -> str:
        return self._encode(
            user_id,
            session_id,
            device,
            "refresh",
            self._refresh_ttl,
        )

    def _encode(
        self,
        user_id: UserId,
        session_id: SessionId,
        device: Device,
        token_type: str,
        ttl_minutes: int,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": user_id.value,
            "sid": session_id.value,
            "dev": device.value,
            "type": token_type,
            "iat": now,
            "exp": now + timedelta(minutes=ttl_minutes),
        }
        return jwt.encode(payload, self._private_key, algorithm=self._algorithm)
