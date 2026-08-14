from __future__ import annotations

from abc import ABC, abstractmethod


class IdempotencyStore(ABC):
    """Records processed event keys to support at-least-once delivery."""

    @abstractmethod
    async def already_processed(self, key: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def mark_processed(self, key: str, event_type: str) -> None:
        raise NotImplementedError
