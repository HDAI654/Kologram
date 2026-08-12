import pytest

from src.domain.value_objects.device import Device
from src.domain.value_objects.session_id import SessionId
from src.domain.value_objects.user_id import UserId
from src.exceptions import TokenInfrastructureError
from src.infrastructure.security.jwt_token_decoder import JwtTokenDecoder
from src.infrastructure.security.jwt_token_encoder import JwtTokenEncoder


def test_decode_and_validate_access() -> None:
    enc = JwtTokenEncoder()
    dec = JwtTokenDecoder()
    uid = UserId.generate()
    sid = SessionId.generate()
    token = enc.create_access_token(uid, sid, Device("web"))
    payload = dec.decode_and_validate(
        enc.FIELD_TYPE_MAP, token, expected_token_type="access"
    )
    assert payload["sub"] == uid.value


def test_decode_wrong_type_raises() -> None:
    enc = JwtTokenEncoder()
    dec = JwtTokenDecoder()
    token = enc.create_refresh_token(
        UserId.generate(), SessionId.generate(), Device("web")
    )
    with pytest.raises(TokenInfrastructureError):
        dec.decode_and_validate(enc.FIELD_TYPE_MAP, token, expected_token_type="access")


def test_decode_garbage_raises() -> None:
    dec = JwtTokenDecoder()
    with pytest.raises(TokenInfrastructureError):
        dec.decode_token("not.a.jwt")
