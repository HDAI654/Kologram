from abc import ABC, abstractmethod
from typing import Any


class TokenDecoder(ABC):
    """Verifies signatures and validates token claims."""

    @abstractmethod
    def decode_token(self, token: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def decode_and_validate(
        self,
        field_type_map: dict,
        token: str,
        expected_token_type: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError
