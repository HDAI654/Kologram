"""Idempotency stores: in-memory (tests) and SQLite (runtime)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from src.domain.ports.idempotency_store import IdempotencyStore

logger = logging.getLogger(__name__)


class InMemoryIdempotencyStore(IdempotencyStore):
    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    async def already_processed(self, key: str) -> bool:
        return key in self._keys

    async def mark_processed(self, key: str, event_type: str) -> None:
        self._keys[key] = event_type


class SQLiteIdempotencyStore(IdempotencyStore):
    """Simple SQLite-backed store via aiosqlite."""

    def __init__(self, path: str) -> None:
        # path may be sqlite+aiosqlite:///file or plain file path
        if path.startswith("sqlite+aiosqlite:///"):
            path = path.removeprefix("sqlite+aiosqlite:///")
        if path == ":memory:":
            self._path = ":memory:"
        else:
            self._path = path
        self._conn = None

    async def connect(self) -> None:
        import aiosqlite

        self._conn = await aiosqlite.connect(self._path)
        await self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_events (
                idempotency_key TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                processed_at TEXT NOT NULL
            )
            """
        )
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def already_processed(self, key: str) -> bool:
        assert self._conn is not None
        cur = await self._conn.execute(
            "SELECT 1 FROM processed_events WHERE idempotency_key = ?",
            (key,),
        )
        row = await cur.fetchone()
        return row is not None

    async def mark_processed(self, key: str, event_type: str) -> None:
        assert self._conn is not None
        now = datetime.now(timezone.utc).isoformat()
        await self._conn.execute(
            """
            INSERT OR IGNORE INTO processed_events
            (idempotency_key, event_type, processed_at) VALUES (?, ?, ?)
            """,
            (key, event_type, now),
        )
        await self._conn.commit()
