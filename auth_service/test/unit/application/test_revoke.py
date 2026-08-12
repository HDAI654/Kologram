from unittest.mock import AsyncMock, MagicMock

import pytest

from src.application.revoke_session import RevokeSessionCommand, RevokeSessionHandler
from src.domain.entities.session import Session
from src.domain.value_objects.user_id import UserId
from src.exceptions import PermissionDeniedError


async def test_revoke_own_session(mock_sessions, mock_decoder, mock_encoder):
    uid = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    target = "33333333-3333-4333-8333-333333333333"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        side_effect=[
            Session.create(user_id=uid.value, device="web", id=sid),
            Session.create(user_id=uid.value, device="ios", id=target),
        ]
    )
    handler = RevokeSessionHandler(mock_sessions, mock_decoder, mock_encoder)
    await handler.handle(
        RevokeSessionCommand(access_token="t", session_id=target, device="web")
    )
    mock_sessions.delete.assert_awaited_once()


async def test_revoke_other_users_session_denied(
    mock_sessions, mock_decoder, mock_encoder
):
    uid = UserId.generate()
    other = UserId.generate()
    sid = "22222222-2222-4222-8222-222222222222"
    target = "33333333-3333-4333-8333-333333333333"
    mock_decoder.decode_and_validate = MagicMock(
        return_value={"sub": uid.value, "sid": sid, "dev": "web", "type": "access"}
    )
    mock_sessions.get_by_id = AsyncMock(
        side_effect=[
            Session.create(user_id=uid.value, device="web", id=sid),
            Session.create(user_id=other.value, device="web", id=target),
        ]
    )
    handler = RevokeSessionHandler(mock_sessions, mock_decoder, mock_encoder)
    with pytest.raises(PermissionDeniedError):
        await handler.handle(
            RevokeSessionCommand(access_token="t", session_id=target, device="web")
        )
