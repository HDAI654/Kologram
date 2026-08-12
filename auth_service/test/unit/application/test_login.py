from unittest.mock import AsyncMock, MagicMock
import pytest
from src.application.login import LoginCommand, LoginHandler, LoginResult
from src.domain.events.user_logged_in import UserLoggedIn
from src.exceptions import InvalidEmailOrPasswordError, UserNotFoundError


async def test_login_success(
    mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_events, sample_user
):
    mock_uow.users.get_by_email = AsyncMock(return_value=sample_user)
    handler = LoginHandler(
        mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_events
    )

    result = await handler.handle(
        LoginCommand(email="trader@example.com", password="secret1A", device="web")
    )

    assert isinstance(result, LoginResult)
    assert result.access_token == "access.jwt"
    mock_sessions.add.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    event = mock_events.publish.await_args.args[0]
    assert isinstance(event, UserLoggedIn)


async def test_login_unknown_user(mock_uow, mock_sessions, mock_encoder, mock_hasher):
    mock_uow.users.get_by_email = AsyncMock(side_effect=UserNotFoundError("missing"))
    handler = LoginHandler(mock_uow, mock_sessions, mock_encoder, mock_hasher)

    with pytest.raises(InvalidEmailOrPasswordError):
        await handler.handle(
            LoginCommand(email="x@y.com", password="secret1A", device="web")
        )


async def test_login_bad_password(
    mock_uow, mock_sessions, mock_encoder, mock_hasher, sample_user
):
    mock_uow.users.get_by_email = AsyncMock(return_value=sample_user)
    mock_hasher.verify = MagicMock(return_value=False)
    handler = LoginHandler(mock_uow, mock_sessions, mock_encoder, mock_hasher)

    with pytest.raises(InvalidEmailOrPasswordError):
        await handler.handle(
            LoginCommand(email="trader@example.com", password="wrong1A", device="web")
        )
