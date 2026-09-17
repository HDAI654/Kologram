import uuid

import pytest

from src.domain.value_objects.listing_id import ListingId
from src.exceptions import InvalidListingIdError


class TestListingId:
    def test_create_valid_uuid(self):
        raw = str(uuid.uuid4())
        assert ListingId(raw).value == raw

    def test_generate_returns_uuid_v4(self):
        assert uuid.UUID(ListingId.generate().value).version == 4

    def test_generate_unique(self):
        assert ListingId.generate() != ListingId.generate()

    def test_strips_whitespace(self):
        raw = str(uuid.uuid4())
        assert ListingId(f"  {raw}  ").value == raw

    def test_rejects_non_string(self):
        for bad in (123, None, b"abc"):
            with pytest.raises(InvalidListingIdError):
                ListingId(bad)  # type: ignore[arg-type]

    def test_rejects_empty_string(self):
        with pytest.raises(InvalidListingIdError):
            ListingId("")

    def test_rejects_whitespace_only(self):
        with pytest.raises(InvalidListingIdError):
            ListingId("   ")

    def test_rejects_invalid_uuid(self):
        with pytest.raises(InvalidListingIdError):
            ListingId("not-a-uuid")

    def test_rejects_invalid_hex(self):
        with pytest.raises(InvalidListingIdError):
            ListingId("gggggggg-gggg-gggg-gggg-gggggggggggg")

    def test_equality_and_hash(self):
        raw = str(uuid.uuid4())
        assert ListingId(raw) == ListingId(raw)
        assert hash(ListingId(raw)) == hash(ListingId(raw))