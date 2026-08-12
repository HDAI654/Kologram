from unittest.mock import AsyncMock
import pytest
from auth_service.src.application.verification_reset_password import (
    VerificationResetPassCommand,
    VerificationResetPassHandler,
)
from src.domain.events.verification_token_created import VerificationTokenCreated


async def test_forget_password_unknown_email_noop(
    mock_uow, mock_token_repo, mock_events
):
    mock_uow.users.exists_by_email = AsyncMock(return_value=False)
    handler = VerificationResetPassHandler(mock_uow, mock_token_repo, mock_events)
    await handler.handle(VerificationResetPassCommand(email="missing@x.com"))
    mock_token_repo.add.assert_not_awaited()
    mock_events.publish.assert_not_awaited()


async def test_forget_password_known_email_publishes_event(
    mock_uow, mock_token_repo, mock_events
):
    mock_uow.users.exists_by_email = AsyncMock(return_value=True)
    handler = VerificationResetPassHandler(mock_uow, mock_token_repo, mock_events)
    await handler.handle(VerificationResetPassCommand(email="a@b.com"))
    mock_token_repo.add.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    event = mock_events.publish.await_args.args[0]
    assert isinstance(event, VerificationTokenCreated)
    assert event.token_type == "forget_pass_verify"
    assert event.email == "a@b.com"
