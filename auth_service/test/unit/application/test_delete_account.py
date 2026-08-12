import pytest
from src.application.delete_account import DeleteAccountHandler, DeleteAccountCommand
from src.exceptions import DeviceMismatchError, SessionNotFoundError
from src.domain.value_objects.user_id import UserId
from src.domain.value_objects.session_id import SessionId
from src.domain.events.account_deleted import AccountDeleted


async def test_delete_account_success(
    mock_uow,
    mock_session_repository,
    mock_token_decoder,
    mock_token_encoder,
    mock_event_publisher,
):
    handler = DeleteAccountHandler(
        uow=mock_uow,
        session_repository=mock_session_repository,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
        event_publisher=mock_event_publisher,
    )
    command = DeleteAccountCommand(access_token="token", device="test-device")

    await handler.handle(command)

    # Token decoded
    mock_token_decoder.decode_and_validate.assert_called_once_with(
        field_type_map=mock_token_encoder.FIELD_TYPE_MAP,
        token="token",
        expected_token_type="access",
    )
    # Session existence checked
    mock_session_repository.get_by_id.assert_awaited_once_with(
        SessionId("22222222-2222-2222-2222-222222222222")
    )
    # User deleted inside UOW
    mock_uow.users.delete.assert_awaited_once_with(
        UserId("11111111-1111-1111-1111-111111111111")
    )
    mock_uow.commit.assert_awaited_once()
    # Sessions deleted outside UOW
    mock_session_repository.delete.assert_awaited_once_with(
        session_id=SessionId("22222222-2222-2222-2222-222222222222"),
        user_id=UserId("11111111-1111-1111-1111-111111111111"),
    )
    mock_session_repository.delete_all_other_sessions.assert_awaited_once_with(
        current_session_id=SessionId("22222222-2222-2222-2222-222222222222"),
        user_id=UserId("11111111-1111-1111-1111-111111111111"),
    )
    # Event published
    mock_event_publisher.publish.assert_awaited_once_with(
        AccountDeleted(user_id="11111111-1111-1111-1111-111111111111")
    )


async def test_delete_account_device_mismatch(
    mock_uow, mock_session_repository, mock_token_decoder, mock_token_encoder
):
    # Override device in token
    mock_token_decoder.decode_and_validate.return_value["dev"] = "different-device"
    handler = DeleteAccountHandler(
        uow=mock_uow,
        session_repository=mock_session_repository,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )
    command = DeleteAccountCommand(access_token="token", device="test-device")

    with pytest.raises(DeviceMismatchError):
        await handler.handle(command)

    # No further calls
    mock_session_repository.get_by_id.assert_not_awaited()
    mock_uow.users.delete.assert_not_awaited()
    mock_uow.commit.assert_not_awaited()


async def test_delete_account_session_not_found(
    mock_uow, mock_session_repository, mock_token_decoder, mock_token_encoder
):
    mock_session_repository.get_by_id.side_effect = SessionNotFoundError
    handler = DeleteAccountHandler(
        uow=mock_uow,
        session_repository=mock_session_repository,
        token_decoder=mock_token_decoder,
        token_encoder=mock_token_encoder,
    )
    command = DeleteAccountCommand(access_token="token", device="test-device")

    with pytest.raises(SessionNotFoundError):
        await handler.handle(command)

    # UOW not entered
    mock_uow.users.delete.assert_not_awaited()
    mock_uow.commit.assert_not_awaited()