"""SQLite-backed idempotency store."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from src.domain.ports.idempotency_store import IdempotencyStore


class SqliteIdempotencyStore(IdempotencyStore):
    def __init__(self, db_path: str) -> None:
        self._path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_events (
                key TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        self._conn.commit()

    def already_processed(self, key: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM processed_events WHERE key = ? LIMIT 1",
            (key,),
        ).fetchone()
        return row is not None

    def mark_processed(self, key: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO processed_events (key) VALUES (?)",
            (key,),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
