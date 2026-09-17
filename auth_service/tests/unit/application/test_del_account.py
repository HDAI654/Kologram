import pytest
from src.application.delete_account import (
    DeleteAccountCommand,
    DeleteAccountHandler,
)
from src.domain.events.account_deleted import AccountDeleted
from src.exceptions import DeviceMismatchError, SessionNotFoundError


@pytest.fixture
def handler(uow, session_repo, decoder, encoder, events) -> DeleteAccountHandler:
    return DeleteAccountHandler(
        uow=uow,
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
        event_publisher=events,
    )


class TestDeleteAccountSuccess:
    async def test_deletes_user_and_commits(
        self,
        handler,
        uow,
        session_repo,
        decoder,
        valid_payload,
        make_user,
        make_session,
    ):
        payload = valid_payload()
        user = make_user(user_id=payload["sub"])
        await uow.users.add(user)
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(
            DeleteAccountCommand(access_token="t", device=payload["dev"])
        )

        assert uow.committed is True
        assert user.id in uow.users.deleted

    async def test_revokes_current_and_all_other_sessions(
        self,
        handler,
        uow,
        session_repo,
        decoder,
        valid_payload,
        make_user,
        make_session,
    ):
        import uuid

        payload = valid_payload()
        user = make_user(user_id=payload["sub"])
        await uow.users.add(user)
        other_sid = str(uuid.uuid4())
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=other_sid)
        )
        decoder.payload = payload

        await handler.handle(
            DeleteAccountCommand(access_token="t", device=payload["dev"])
        )

        assert (payload["sid"], payload["sub"]) in session_repo.deleted
        assert (payload["sid"], payload["sub"]) in session_repo.delete_other_calls
        assert other_sid not in session_repo._store

    async def test_publishes_account_deleted(
        self,
        handler,
        uow,
        session_repo,
        decoder,
        events,
        valid_payload,
        make_user,
        make_session,
    ):
        payload = valid_payload()
        user = make_user(user_id=payload["sub"])
        await uow.users.add(user)
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(
            DeleteAccountCommand(access_token="t", device=payload["dev"])
        )

        assert len(events.published) == 1
        assert isinstance(events.published[0], AccountDeleted)
        assert events.published[0].user_id == payload["sub"]


class TestDeleteAccountFailures:
    async def test_device_mismatch_prevents_deletion(
        self,
        handler,
        uow,
        session_repo,
        decoder,
        valid_payload,
        make_user,
        make_session,
    ):
        payload = valid_payload(device="iPhone 15")
        user = make_user(user_id=payload["sub"])
        await uow.users.add(user)
        await session_repo.add(
            make_session(
                user_id=payload["sub"], session_id=payload["sid"], device="iPhone 15"
            )
        )
        decoder.payload = payload

        with pytest.raises(DeviceMismatchError):
            await handler.handle(
                DeleteAccountCommand(access_token="t", device="DifferentDevice")
            )

        assert uow.committed is False
        assert uow.users.deleted == []

    async def test_missing_session_prevents_user_deletion(
        self, handler, uow, decoder, valid_payload, make_user
    ):
        payload = valid_payload()
        user = make_user(user_id=payload["sub"])
        await uow.users.add(user)
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                DeleteAccountCommand(access_token="t", device=payload["dev"])
            )

        assert uow.committed is False
        assert uow.users.deleted == []

    async def test_missing_user_rolls_back(
        self, handler, uow, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        with pytest.raises(Exception):
            await handler.handle(
                DeleteAccountCommand(access_token="t", device=payload["dev"])
            )

        assert uow.committed is False
        assert uow.rolled_back is True
