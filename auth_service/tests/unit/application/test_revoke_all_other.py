import uuid
import pytest
from src.application.revoke_all_other_sessions import (
    RevokeAllOtherSessionsCommand,
    RevokeAllOtherSessionsHandler,
)
from src.exceptions import DeviceMismatchError, SessionNotFoundError


@pytest.fixture
def handler(session_repo, decoder, encoder) -> RevokeAllOtherSessionsHandler:
    return RevokeAllOtherSessionsHandler(
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
    )


class TestRevokeAllOtherSessionsSuccess:
    async def test_delegates_with_current_session_and_user(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(
            RevokeAllOtherSessionsCommand(access_token="t", device=payload["dev"])
        )

        assert session_repo.delete_other_calls == [(payload["sid"], payload["sub"])]

    async def test_removes_all_other_sessions_keeps_current(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        other_id = str(uuid.uuid4())
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=other_id)
        )
        decoder.payload = payload

        await handler.handle(
            RevokeAllOtherSessionsCommand(access_token="t", device=payload["dev"])
        )

        assert other_id not in session_repo._store
        assert payload["sid"] in session_repo._store


class TestRevokeAllOtherSessionsFailures:
    async def test_missing_current_session_raises(
        self, handler, session_repo, decoder, valid_payload
    ):
        payload = valid_payload()
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                RevokeAllOtherSessionsCommand(access_token="t", device=payload["dev"])
            )
        assert session_repo.delete_other_calls == []

    async def test_device_mismatch_raises_and_does_not_revoke(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload(device="iPhone 15")
        await session_repo.add(
            make_session(
                user_id=payload["sub"], session_id=payload["sid"], device="iPhone 15"
            )
        )
        decoder.payload = payload

        with pytest.raises(DeviceMismatchError):
            await handler.handle(
                RevokeAllOtherSessionsCommand(access_token="t", device="Different")
            )
        assert session_repo.delete_other_calls == []
