from unittest.mock import AsyncMock, MagicMock
import pytest
from src.application.rotate_tokens import RotateTokensCommand, RotateTokensHandler
from src.domain.entities.session import Session
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError


async def test_rotate_access_only(mock_sessions, mock_decoder, mock_encoder):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={
            "sub": uid.value,
            "sid": sid,
            "dev": "web",
            "type": "refresh",
            "exp": 9999999999,
        }
    )
    mock_sessions.get_by_id = AsyncMock(
        return_value=Session.create(user_id=uid.value, device="web", id=sid)
    )
    handler = RotateTokensHandler(mock_sessions, mock_decoder, mock_encoder)
    result = await handler.handle(RotateTokensCommand(refresh_token="r", device="web"))
    assert result.access_token == "access.jwt"
    assert result.refresh_token is None


async def test_rotate_device_mismatch(mock_sessions, mock_decoder, mock_encoder):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={
            "sub": uid.value,
            "sid": sid,
            "dev": "web",
            "type": "refresh",
            "exp": 9999999999,
        }
    )
    handler = RotateTokensHandler(mock_sessions, mock_decoder, mock_encoder)
    with pytest.raises(DeviceMismatchError):
        await handler.handle(RotateTokensCommand(refresh_token="r", device="ios"))
