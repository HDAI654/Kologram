from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.revoke_all_other_sessions import (
    RevokeAllOtherSessionsCommand,
    RevokeAllOtherSessionsHandler,
)
from src.domain.entities.session import Session
from src.domain.value_objects.user_id import UserId


async def test_revoke_all_other(mock_sessions, mock_decoder, mock_encoder):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        return_value=Session.create(user_id=uid.value, device="web", id=sid)
    )
    handler = RevokeAllOtherSessionsHandler(mock_sessions, mock_decoder, mock_encoder)
    await handler.handle(RevokeAllOtherSessionsCommand(access_token="t", device="web"))
    mock_sessions.delete_all_other_sessions.assert_awaited_once()
