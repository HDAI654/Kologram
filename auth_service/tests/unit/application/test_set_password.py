import pytest
from src.application.set_password import (
    SetPasswordCommand,
    SetPasswordHandler,
)
from src.exceptions import (
    DeviceMismatchError,
    InvalidPasswordError,
    SessionNotFoundError,
    UserNotFoundError,
)


@pytest.fixture
def handler(uow, session_repo, decoder, encoder, hasher) -> SetPasswordHandler:
    return SetPasswordHandler(
        uow=uow,
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
        password_hasher=hasher,
    )


class TestSetPasswordSuccess:
    async def test_updates_password_and_commits(
        self,
        handler,
        uow,
        session_repo,
        decoder,
        hasher,
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
            SetPasswordCommand(
                access_token="t", new_password="newpass1", device=payload["dev"]
            )
        )

        assert uow.committed is True
        assert hasher.hash_calls == ["newpass1"]
        assert uow.users.updated[0][0] == user.id

    async def test_revokes_other_sessions(
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
            SetPasswordCommand(
                access_token="t", new_password="newpass1", device=payload["dev"]
            )
        )

        assert (payload["sid"], payload["sub"]) in session_repo.delete_other_calls


class TestSetPasswordFailures:
    async def test_missing_current_session_raises(
        self, handler, uow, decoder, valid_payload
    ):
        payload = valid_payload()
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                SetPasswordCommand(
                    access_token="t", new_password="newpass1", device=payload["dev"]
                )
            )
        assert uow.committed is False

    async def test_device_mismatch_raises(
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
                SetPasswordCommand(
                    access_token="t", new_password="newpass1", device="Different"
                )
            )
        assert uow.committed is False

    async def test_invalid_password_rejected_before_uow(
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

        with pytest.raises(InvalidPasswordError):
            await handler.handle(
                SetPasswordCommand(
                    access_token="t", new_password="short", device=payload["dev"]
                )
            )
        assert uow.committed is False
        assert uow.users.updated == []

    async def test_missing_user_rolls_back(
        self, handler, uow, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        with pytest.raises(UserNotFoundError):
            await handler.handle(
                SetPasswordCommand(
                    access_token="t", new_password="newpass1", device=payload["dev"]
                )
            )

        assert uow.committed is False
        assert uow.rolled_back is True
