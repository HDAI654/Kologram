from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.set_password import SetPasswordCommand, SetPasswordHandler
from src.domain.entities.session import Session
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError


async def test_set_password_success(
    mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_hasher
):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        return_value=Session.create(user_id=uid.value, device="web", id=sid)
    )
    handler = SetPasswordHandler(
        mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_hasher
    )
    await handler.handle(
        SetPasswordCommand(access_token="tok", new_password="Newpass1", device="web")
    )
    mock_uow.users.update.assert_awaited_once()
    mock_sessions.delete_all_other_sessions.assert_awaited_once()


async def test_set_password_device_mismatch(
    mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_hasher
):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        return_value=Session.create(user_id=uid.value, device="web", id=sid)
    )
    handler = SetPasswordHandler(
        mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_hasher
    )
    with pytest.raises(DeviceMismatchError):
        await handler.handle(
            SetPasswordCommand(
                access_token="tok", new_password="Newpass1", device="ios"
            )
        )
