"""RS256 JWT token decoder."""

from __future__ import annotations

from typing import Any

import jwt

from src.conf import Config
from src.domain.ports.token_decoder import TokenDecoder
from src.exceptions import TokenInfrastructureError


class JwtTokenDecoder(TokenDecoder):
    def __init__(
        self,
        public_key: str | None = None,
        algorithm: str | None = None,
    ) -> None:
        self._public_key = public_key or Config.AUTH_TOKEN_PUBLIC_KEY
        self._algorithm = algorithm or Config.AUTH_TOKEN_ALGORITHM

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._public_key,
                algorithms=[self._algorithm],
            )
        except jwt.PyJWTError as exc:
            raise TokenInfrastructureError(f"Invalid token: {exc}") from exc

    def decode_and_validate(
        self,
        field_type_map: dict,
        token: str,
        expected_token_type: str | None = None,
    ) -> dict[str, Any]:
        payload = self.decode_token(token)
        if expected_token_type is not None:
            actual = payload.get("type")
            if actual != expected_token_type:
                raise TokenInfrastructureError(
                    f"Expected token type '{expected_token_type}', got '{actual}'"
                )
        for field, expected in field_type_map.items():
            if field not in payload:
                continue
            value = payload[field]
            if isinstance(expected, tuple):
                if not isinstance(value, expected):
                    raise TokenInfrastructureError(
                        f"Claim '{field}' has unexpected type"
                    )
            elif not isinstance(value, expected):
                raise TokenInfrastructureError(f"Claim '{field}' has unexpected type")
        return payload
