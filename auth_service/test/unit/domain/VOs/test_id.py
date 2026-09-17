import uuid
import pytest
from src.domain.value_objects.id_vo import ID
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.verification_token import VerificationToken
from src.exceptions import (
    InvalidSessionIdError,
    InvalidUserIdError,
    InvalidVerificationTokenError,
)

_ID_CASES = [
    pytest.param(SessionId, InvalidSessionIdError, id="SessionId"),
    pytest.param(UserId, InvalidUserIdError, id="UserId"),
    pytest.param(
        VerificationToken, InvalidVerificationTokenError, id="VerificationToken"
    ),
]


class TestSubclassConstruction:
    @pytest.mark.parametrize("vo_cls, _exc", _ID_CASES)
    def test_accepts_valid_v4_uuid(self, vo_cls, _exc):
        raw = str(uuid.uuid4())
        assert vo_cls(raw).value == raw

    @pytest.mark.parametrize("vo_cls, _exc", _ID_CASES)
    def test_strips_whitespace(self, vo_cls, _exc):
        raw = str(uuid.uuid4())
        assert vo_cls(f"  {raw}  ").value == raw

    @pytest.mark.parametrize("vo_cls, _exc", _ID_CASES)
    def test_generate_returns_v4(self, vo_cls, _exc):
        assert uuid.UUID(vo_cls.generate().value).version == 4

    @pytest.mark.parametrize("vo_cls, _exc", _ID_CASES)
    def test_generate_unique(self, vo_cls, _exc):
        assert vo_cls.generate() != vo_cls.generate()


class TestSubclassRejections:
    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    @pytest.mark.parametrize("value", [123, None, b"abc", 1.5])
    def test_non_string_rejected(self, vo_cls, exc_cls, value):
        with pytest.raises(exc_cls):
            vo_cls(value)  # type: ignore[arg-type]

    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    def test_empty_string_rejected(self, vo_cls, exc_cls):
        with pytest.raises(exc_cls):
            vo_cls("")

    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    def test_whitespace_only_rejected(self, vo_cls, exc_cls):
        with pytest.raises(exc_cls):
            vo_cls("   ")

    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    def test_malformed_uuid_rejected(self, vo_cls, exc_cls):
        with pytest.raises(exc_cls):
            vo_cls("not-a-uuid")

    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    def test_truncated_uuid_rejected(self, vo_cls, exc_cls):
        with pytest.raises(exc_cls):
            vo_cls("12345678-1234-4123-8123-12345678901")

    @pytest.mark.parametrize("vo_cls, exc_cls", _ID_CASES)
    def test_non_hex_uuid_rejected(self, vo_cls, exc_cls):
        with pytest.raises(exc_cls):
            vo_cls("gggggggg-gggg-4ggg-8ggg-gggggggggggg")


class TestSubclassIdentity:
    @pytest.mark.parametrize("vo_cls, _exc", _ID_CASES)
    def test_equality_and_hash(self, vo_cls, _exc):
        raw = str(uuid.uuid4())
        assert vo_cls(raw) == vo_cls(raw)
        assert hash(vo_cls(raw)) == hash(vo_cls(raw))

    def test_different_subclasses_with_same_uuid_are_not_equal(self):
        """``BaseVO.__eq__`` requires ``self.__class__ is other.__class__``."""
        raw = str(uuid.uuid4())
        assert SessionId(raw) != UserId(raw)
        assert UserId(raw) != VerificationToken(raw)
