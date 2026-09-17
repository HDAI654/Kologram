import jwt
import pytest

from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.infrastructure.security.jwt_token_encoder import JwtTokenEncoder

SECRET = "test-secret-key-do-not-use-in-production-please-32bytes-min"


@pytest.fixture
def encoder() -> JwtTokenEncoder:
    return JwtTokenEncoder(private_key=SECRET, algorithm="HS256")


@pytest.fixture
def identities():
    return (
        UserId.generate(),
        SessionId.generate(),
        Device("iPhone 15"),
    )


class TestAccessToken:
    def test_produces_decodable_jwt(self, encoder, identities):
        user_id, session_id, device = identities
        token = encoder.create_access_token(user_id, session_id, device)
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        assert payload["sub"] == user_id.value
        assert payload["sid"] == session_id.value
        assert payload["dev"] == device.value
        assert payload["type"] == "access"

    def test_has_exp_and_iat(self, encoder, identities):
        user_id, session_id, device = identities
        payload = jwt.decode(
            encoder.create_access_token(user_id, session_id, device),
            SECRET,
            algorithms=["HS256"],
        )
        assert "exp" in payload
        assert "iat" in payload
        assert payload["exp"] > payload["iat"]


class TestRefreshToken:
    def test_produces_decodable_jwt(self, encoder, identities):
        user_id, session_id, device = identities
        token = encoder.create_refresh_token(user_id, session_id, device)
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        assert payload["type"] == "refresh"
        assert payload["sub"] == user_id.value

    def test_refresh_ttl_greater_than_access(self, encoder, identities):
        user_id, session_id, device = identities
        access = jwt.decode(
            encoder.create_access_token(user_id, session_id, device),
            SECRET,
            algorithms=["HS256"],
        )
        refresh = jwt.decode(
            encoder.create_refresh_token(user_id, session_id, device),
            SECRET,
            algorithms=["HS256"],
        )
        assert refresh["exp"] >= access["exp"]


class TestCustomTTL:
    def test_custom_access_ttl_is_respected(self, identities):
        user_id, session_id, device = identities
        encoder = JwtTokenEncoder(
            private_key=SECRET, algorithm="HS256", access_ttl_minutes=5
        )
        payload = jwt.decode(
            encoder.create_access_token(user_id, session_id, device),
            SECRET,
            algorithms=["HS256"],
        )
        assert payload["exp"] - payload["iat"] == 5 * 60

    def test_custom_refresh_ttl_is_respected(self, identities):
        user_id, session_id, device = identities
        encoder = JwtTokenEncoder(
            private_key=SECRET, algorithm="HS256", refresh_ttl_minutes=10
        )
        payload = jwt.decode(
            encoder.create_refresh_token(user_id, session_id, device),
            SECRET,
            algorithms=["HS256"],
        )
        assert payload["exp"] - payload["iat"] == 10 * 60


class TestFieldTypeMap:
    def test_field_type_map_contains_expected_keys(self):
        for key in ("sub", "sid", "dev", "type", "exp", "iat"):
            assert key in JwtTokenEncoder.FIELD_TYPE_MAP