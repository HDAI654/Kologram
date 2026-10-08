from __future__ import annotations

from src.infrastructure.persistence.sqlite_idempotency import SqliteIdempotencyStore


def test_sqlite_idempotency_roundtrip(tmp_path) -> None:
    path = str(tmp_path / "id.sqlite3")
    store = SqliteIdempotencyStore(path)
    assert store.already_processed("a") is False
    store.mark_processed("a")
    assert store.already_processed("a") is True
    store.close()
