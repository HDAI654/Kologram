import uuid

import pytest

from src.domain.value_objects.user_id import UserId
from src.exceptions import InvalidUserIdError


class TestUserId:
    def test_create_valid_uuid(self):
        raw = str(uuid.uuid4())
        assert UserId(raw).value == raw

    def test_generate_returns_uuid_v4(self):
        assert uuid.UUID(UserId.generate().value).version == 4

    def test_generate_unique(self):
        assert UserId.generate() != UserId.generate()

    def test_strips_whitespace(self):
        raw = str(uuid.uuid4())
        assert UserId(f"  {raw}  ").value == raw

    def test_rejects_non_string(self):
        for bad in (123, None, b"abc"):
            with pytest.raises(InvalidUserIdError):
                UserId(bad)  # type: ignore[arg-type]

    def test_rejects_empty_string(self):
        with pytest.raises(InvalidUserIdError):
            UserId("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(InvalidUserIdError):
            UserId("   ")

    def test_rejects_invalid_uuid(self):
        with pytest.raises(InvalidUserIdError):
            UserId("not-a-uuid")

    def test_equality_and_hash(self):
        raw = str(uuid.uuid4())
        assert UserId(raw) == UserId(raw)
        assert hash(UserId(raw)) == hash(UserId(raw))