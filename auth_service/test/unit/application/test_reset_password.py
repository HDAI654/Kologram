from unittest.mock import AsyncMock

import pytest

from src.application.reset_password import ResetPasswordCommand, ResetPasswordHandler
from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.exceptions import InvalidVerificationTokenError


async def test_reset_password_success(mock_uow, mock_hasher, mock_token_repo):
    user = User.create(email="a@b.com", hashed_password="old")
    mock_token_repo.get = AsyncMock(return_value=Email("a@b.com"))
    mock_uow.users.get_by_email = AsyncMock(return_value=user)
    handler = ResetPasswordHandler(mock_uow, mock_hasher, mock_token_repo)
    await handler.handle(
        ResetPasswordCommand(
            verify_token="11111111-1111-4111-8111-111111111111",
            new_password="newpass1",
        )
    )
    mock_uow.users.update.assert_awaited_once()
    mock_uow.commit.assert_awaited_once()
    mock_token_repo.delete.assert_awaited_once()


async def test_reset_password_bad_token(mock_uow, mock_hasher, mock_token_repo):
    mock_token_repo.get = AsyncMock(return_value=None)
    handler = ResetPasswordHandler(mock_uow, mock_hasher, mock_token_repo)
    with pytest.raises(InvalidVerificationTokenError):
        await handler.handle(
            ResetPasswordCommand(
                verify_token="11111111-1111-4111-8111-111111111111",
                new_password="newpass1",
            )
        )
