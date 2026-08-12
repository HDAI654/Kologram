from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.logout import LogoutCommand, LogoutHandler
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError


async def test_logout_success(mock_sessions, mock_decoder, mock_encoder, mock_events):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    handler = LogoutHandler(mock_sessions, mock_decoder, mock_encoder, mock_events)
    await handler.handle(LogoutCommand(access_token="tok", device="web"))
    mock_sessions.delete.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


async def test_logout_device_mismatch(mock_sessions, mock_decoder, mock_encoder):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    handler = LogoutHandler(mock_sessions, mock_decoder, mock_encoder)
    with pytest.raises(DeviceMismatchError):
        await handler.handle(LogoutCommand(access_token="tok", device="ios"))
