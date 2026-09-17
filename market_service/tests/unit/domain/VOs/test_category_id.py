import uuid

import pytest

from src.domain.value_objects.category_id import CategoryId
from src.exceptions import InvalidCategoryIdError


class TestCategoryId:
    def test_create_valid_uuid(self):
        raw = str(uuid.uuid4())
        assert CategoryId(raw).value == raw

    def test_generate_returns_uuid_v4(self):
        assert uuid.UUID(CategoryId.generate().value).version == 4

    def test_generate_unique(self):
        assert CategoryId.generate() != CategoryId.generate()

    def test_strips_whitespace(self):
        raw = str(uuid.uuid4())
        assert CategoryId(f"  {raw}  ").value == raw

    def test_rejects_non_string(self):
        for bad in (123, None, b"abc", 1.5):
            with pytest.raises(InvalidCategoryIdError):
                CategoryId(bad)  # type: ignore[arg-type]

    def test_rejects_empty_string(self):
        with pytest.raises(InvalidCategoryIdError):
            CategoryId("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(InvalidCategoryIdError):
            CategoryId("   ")

    def test_rejects_invalid_uuid(self):
        with pytest.raises(InvalidCategoryIdError):
            CategoryId("not-a-uuid")

    def test_rejects_malformed_uuid(self):
        with pytest.raises(InvalidCategoryIdError):
            CategoryId("12345678-1234-1234-1234-12345678901")

    def test_rejects_invalid_hex(self):
        with pytest.raises(InvalidCategoryIdError):
            CategoryId("gggggggg-gggg-gggg-gggg-gggggggggggg")

    def test_equality_and_hash(self):
        raw = str(uuid.uuid4())
        assert CategoryId(raw) == CategoryId(raw)
        assert hash(CategoryId(raw)) == hash(CategoryId(raw))
