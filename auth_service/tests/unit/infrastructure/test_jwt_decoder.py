from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.exceptions import TokenInfrastructureError
from src.infrastructure.security.jwt_token_decoder import JwtTokenDecoder

SECRET = "test-secret-key-do-not-use-in-production-please-32bytes-min"

FIELD_TYPE_MAP = {
    "sub": str,
    "sid": str,
    "dev": str,
    "type": str,
    "exp": (int, float),
    "iat": (int, float),
}


@pytest.fixture
def decoder() -> JwtTokenDecoder:
    return JwtTokenDecoder(public_key=SECRET, algorithm="HS256")


def _token(**overrides) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "u-1",
        "sid": "s-1",
        "dev": "iPhone",
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=5),
    }
    payload.update(overrides)
    return jwt.encode(payload, SECRET, algorithm="HS256")


class TestDecodeToken:
    def test_valid_token_returns_payload(self, decoder):
        payload = decoder.decode_token(_token())
        assert payload["sub"] == "u-1"
        assert payload["type"] == "access"

    def test_invalid_signature_raises(self, decoder):
        other = jwt.encode({"sub": "u-1"}, "different-secret", algorithm="HS256")
        with pytest.raises(TokenInfrastructureError):
            decoder.decode_token(other)

    def test_malformed_token_raises(self, decoder):
        with pytest.raises(TokenInfrastructureError):
            decoder.decode_token("not-a-jwt")

    def test_expired_token_raises(self, decoder):
        expired = _token(exp=datetime.now(timezone.utc) - timedelta(seconds=1))
        with pytest.raises(TokenInfrastructureError):
            decoder.decode_token(expired)

    def test_preserves_cause(self, decoder):
        with pytest.raises(TokenInfrastructureError) as exc_info:
            decoder.decode_token("not-a-jwt")
        assert exc_info.value.__cause__ is not None


class TestDecodeAndValidate:
    def test_accepts_matching_token_type(self, decoder):
        payload = decoder.decode_and_validate(
            field_type_map=FIELD_TYPE_MAP,
            token=_token(type="access"),
            expected_token_type="access",
        )
        assert payload["type"] == "access"

    def test_rejects_wrong_token_type(self, decoder):
        with pytest.raises(TokenInfrastructureError):
            decoder.decode_and_validate(
                field_type_map=FIELD_TYPE_MAP,
                token=_token(type="refresh"),
                expected_token_type="access",
            )

    def test_no_expected_type_skips_type_check(self, decoder):
        payload = decoder.decode_and_validate(
            field_type_map=FIELD_TYPE_MAP, token=_token(type="anything")
        )
        assert payload["type"] == "anything"

    def test_rejects_wrong_claim_type(self, decoder):
        with pytest.raises(TokenInfrastructureError):
            decoder.decode_and_validate(
                field_type_map=FIELD_TYPE_MAP,
                token=_token(sub=123),  # sub is int but map expects str
            )

    def test_missing_claim_is_skipped(self, decoder):
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {"sub": "u-1", "exp": now + timedelta(minutes=5)},
            SECRET,
            algorithm="HS256",
        )
        payload = decoder.decode_and_validate(
            field_type_map=FIELD_TYPE_MAP, token=token
        )
        assert payload["sub"] == "u-1"

    def test_numeric_range_type_accepts_float_and_int(self, decoder):
        now = datetime.now(timezone.utc).timestamp()
        payload = decoder.decode_and_validate(
            field_type_map=FIELD_TYPE_MAP,
            token=_token(exp=now + 60, iat=now),
        )
        assert isinstance(payload["exp"], (int, float))
