from unittest.mock import AsyncMock

import pytest

from src.application.send_verification import (
    SendVerificationCommand,
    SendVerificationHandler,
)
from src.domain.events.verification_token_created import VerificationTokenCreated
from src.exceptions import EmailBlockedError


async def test_send_verification_publishes_event(
    mock_token_repo, mock_events, mock_blocklist
):
    handler = SendVerificationHandler(mock_token_repo, mock_events, mock_blocklist)
    await handler.handle(SendVerificationCommand(email="a@b.com"))
    mock_token_repo.add.assert_awaited_once()
    mock_events.publish.assert_awaited_once()
    event = mock_events.publish.await_args.args[0]
    assert isinstance(event, VerificationTokenCreated)
    assert event.email == "a@b.com"
    assert event.token_type == "verifyemail"
    assert event.token


async def test_send_verification_blocked(mock_token_repo, mock_events, mock_blocklist):
    mock_blocklist.is_blocked = AsyncMock(return_value=True)
    handler = SendVerificationHandler(mock_token_repo, mock_events, mock_blocklist)
    with pytest.raises(EmailBlockedError):
        await handler.handle(SendVerificationCommand(email="bad@b.com"))
    mock_events.publish.assert_not_awaited()
