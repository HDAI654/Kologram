"""Port: process-once guarantee for consumed broker messages."""

from __future__ import annotations

from abc import ABC, abstractmethod


class IdempotencyStore(ABC):
    @abstractmethod
    def already_processed(self, key: str) -> bool:
        ...

    @abstractmethod
    def mark_processed(self, key: str) -> None:
        ...
