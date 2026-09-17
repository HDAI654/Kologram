import pytest
from src.application.logout import LogoutCommand, LogoutHandler
from src.domain.events.user_logged_out import UserLoggedOut
from src.exceptions import DeviceMismatchError, SessionNotFoundError


@pytest.fixture
def handler(session_repo, decoder, encoder, events) -> LogoutHandler:
    return LogoutHandler(
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
        event_publisher=events,
    )


class TestLogoutSuccess:
    async def test_deletes_current_session(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(LogoutCommand(access_token="token", device=payload["dev"]))

        assert (payload["sid"], payload["sub"]) in session_repo.deleted

    async def test_decodes_as_access_token(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(LogoutCommand(access_token="xyz", device=payload["dev"]))

        assert decoder.calls[0]["expected_token_type"] == "access"
        assert decoder.calls[0]["token"] == "xyz"

    async def test_publishes_user_logged_out(
        self, handler, session_repo, decoder, events, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(LogoutCommand(access_token="t", device=payload["dev"]))

        assert len(events.published) == 1
        event = events.published[0]
        assert isinstance(event, UserLoggedOut)
        assert event.user_id == payload["sub"]
        assert event.session_id == payload["sid"]
        assert event.device == payload["dev"]

    async def test_no_publisher_still_revokes(
        self, session_repo, decoder, encoder, valid_payload, make_session
    ):
        handler = LogoutHandler(
            session_repository=session_repo,
            token_decoder=decoder,
            token_encoder=encoder,
            event_publisher=None,
        )
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(LogoutCommand(access_token="t", device=payload["dev"]))
        assert (payload["sid"], payload["sub"]) in session_repo.deleted


class TestLogoutFailures:
    async def test_device_mismatch_raises_and_does_not_delete(
        self, handler, session_repo, decoder, events, valid_payload, make_session
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
                LogoutCommand(access_token="t", device="DifferentDevice")
            )
        assert session_repo.deleted == []
        assert events.published == []

    async def test_missing_session_raises(
        self, handler, decoder, events, valid_payload
    ):
        payload = valid_payload()
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(LogoutCommand(access_token="t", device=payload["dev"]))
        assert events.published == []
