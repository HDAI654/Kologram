from unittest.mock import AsyncMock, MagicMock
import pytest
from src.application.delete_account import DeleteAccountCommand, DeleteAccountHandler
from src.domain.entities.session import Session
from src.domain.events.account_deleted import AccountDeleted
from src.domain.value_objects.user_id import UserId
from src.exceptions import DeviceMismatchError


async def test_delete_account_success(
    mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_events
):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        return_value=Session.create(user_id=uid.value, device="web", id=sid)
    )
    handler = DeleteAccountHandler(
        mock_uow, mock_sessions, mock_decoder, mock_encoder, mock_events
    )
    await handler.handle(DeleteAccountCommand(access_token="tok", device="web"))
    mock_uow.users.delete.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    assert isinstance(mock_events.publish.await_args.args[0], AccountDeleted)


async def test_delete_account_device_mismatch(
    mock_uow, mock_sessions, mock_decoder, mock_encoder
):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    handler = DeleteAccountHandler(mock_uow, mock_sessions, mock_decoder, mock_encoder)
    with pytest.raises(DeviceMismatchError):
        await handler.handle(DeleteAccountCommand(access_token="tok", device="ios"))
