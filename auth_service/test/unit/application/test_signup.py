from unittest.mock import AsyncMock

import pytest

from src.application.signup import SignupCommand, SignupHandler, SignupResult
from src.domain.value_objects.email import Email
from src.exceptions import InvalidVerificationTokenError


async def test_signup_success(
    mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_token_repo, mock_events
):
    mock_token_repo.get = AsyncMock(return_value=Email("new@example.com"))
    mock_token_repo.delete = AsyncMock()
    handler = SignupHandler(
        mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_token_repo, mock_events
    )

    result = await handler.handle(
        SignupCommand(
            verify_token="11111111-1111-4111-8111-111111111111",
            password="secret1A",
            device="ios",
        )
    )

    assert isinstance(result, SignupResult)
    mock_uow.users.add.assert_awaited_once()
    mock_sessions.add.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_events.publish.assert_awaited_once()


async def test_signup_invalid_token(
    mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_token_repo
):
    mock_token_repo.get = AsyncMock(return_value=None)
    handler = SignupHandler(
        mock_uow, mock_sessions, mock_encoder, mock_hasher, mock_token_repo
    )

    with pytest.raises(InvalidVerificationTokenError):
        await handler.handle(
            SignupCommand(
                verify_token="11111111-1111-4111-8111-111111111111",
                password="secret1A",
                device="ios",
            )
        )
