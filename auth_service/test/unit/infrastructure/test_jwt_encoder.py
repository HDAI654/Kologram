import jwt
from src.conf import Config
from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.infrastructure.security.jwt_token_encoder import JwtTokenEncoder


def test_create_access_token_claims() -> None:
    enc = JwtTokenEncoder()
    uid = UserId.generate()
    sid = SessionId.generate()
    token = enc.create_access_token(uid, sid, Device("web"))
    payload = jwt.decode(
        token, Config.AUTH_TOKEN_PUBLIC_KEY, algorithms=[Config.AUTH_TOKEN_ALGORITHM]
    )
    assert payload["sub"] == uid.value
    assert payload["sid"] == sid.value
    assert payload["dev"] == "web"
    assert payload["type"] == "access"


def test_create_refresh_token_type() -> None:
    enc = JwtTokenEncoder()
    token = enc.create_refresh_token(
        UserId.generate(), SessionId.generate(), Device("ios")
    )
    payload = jwt.decode(
        token, Config.AUTH_TOKEN_PUBLIC_KEY, algorithms=[Config.AUTH_TOKEN_ALGORITHM]
    )
    assert payload["type"] == "refresh"
