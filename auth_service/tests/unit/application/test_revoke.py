import uuid
import pytest
from src.application.revoke_session import (
    RevokeSessionCommand,
    RevokeSessionHandler,
)
from src.exceptions import (
    DeviceMismatchError,
    PermissionDeniedError,
    SessionNotFoundError,
)


@pytest.fixture
def handler(session_repo, decoder, encoder) -> RevokeSessionHandler:
    return RevokeSessionHandler(
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
    )


class TestRevokeSessionSuccess:
    async def test_revokes_owned_session(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        target_id = str(uuid.uuid4())
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=target_id)
        )
        decoder.payload = payload

        await handler.handle(
            RevokeSessionCommand(
                access_token="t",
                session_id=target_id,
                device=payload["dev"],
            )
        )

        assert (target_id, payload["sub"]) in session_repo.deleted

    async def test_can_revoke_own_current_session(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(
            RevokeSessionCommand(
                access_token="t",
                session_id=payload["sid"],
                device=payload["dev"],
            )
        )

        assert (payload["sid"], payload["sub"]) in session_repo.deleted


class TestRevokeSessionFailures:
    async def test_missing_current_session_raises(
        self, handler, decoder, valid_payload
    ):
        payload = valid_payload()
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                RevokeSessionCommand(
                    access_token="t",
                    session_id=payload["sid"],
                    device=payload["dev"],
                )
            )

    async def test_device_mismatch_raises(
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
                RevokeSessionCommand(
                    access_token="t",
                    session_id=payload["sid"],
                    device="Different",
                )
            )
        assert session_repo.deleted == []

    async def test_cross_user_target_forbidden(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        foreign_owner = str(uuid.uuid4())
        foreign_sid = str(uuid.uuid4())
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        await session_repo.add(
            make_session(user_id=foreign_owner, session_id=foreign_sid)
        )
        decoder.payload = payload

        with pytest.raises(PermissionDeniedError):
            await handler.handle(
                RevokeSessionCommand(
                    access_token="t",
                    session_id=foreign_sid,
                    device=payload["dev"],
                )
            )
        assert session_repo.deleted == []

    async def test_unknown_target_session_raises(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                RevokeSessionCommand(
                    access_token="t",
                    session_id=str(uuid.uuid4()),
                    device=payload["dev"],
                )
            )
