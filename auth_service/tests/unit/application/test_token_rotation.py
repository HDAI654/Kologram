from datetime import datetime, timedelta, timezone
import pytest
from src.application.rotate_tokens import (
    RotateTokensCommand,
    RotateTokensHandler,
)
from src.conf import Config
from src.exceptions import DeviceMismatchError, SessionNotFoundError


@pytest.fixture
def handler(session_repo, decoder, encoder) -> RotateTokensHandler:
    return RotateTokensHandler(
        session_repository=session_repo,
        token_decoder=decoder,
        token_encoder=encoder,
    )


def _exp_in(hours: float) -> float:
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).timestamp()


class TestRotateTokensSuccess:
    async def test_always_mints_new_access_token(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload(exp=_exp_in(24 * 30))
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        result = await handler.handle(
            RotateTokensCommand(refresh_token="t", device=payload["dev"])
        )

        assert result.access_token.startswith(f"access::{payload['sub']}")

    async def test_no_refresh_rotation_when_far_from_expiry(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload(exp=_exp_in(24 * 30))
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        result = await handler.handle(
            RotateTokensCommand(refresh_token="t", device=payload["dev"])
        )

        assert result.refresh_token is None
        assert session_repo.extended == []

    async def test_rotates_refresh_near_expiry(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        # 30 s before expiry, well inside the rotate threshold.
        payload = valid_payload(exp=_exp_in(0.5 / 60))
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        result = await handler.handle(
            RotateTokensCommand(refresh_token="t", device=payload["dev"])
        )

        assert result.refresh_token is not None
        assert result.refresh_token.startswith(f"refresh::{payload['sub']}")
        assert session_repo.extended == [payload["sid"]]

    async def test_decodes_as_refresh_token(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload(exp=_exp_in(24 * 30))
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        await handler.handle(
            RotateTokensCommand(refresh_token="refresh-value", device=payload["dev"])
        )

        assert decoder.calls[0]["expected_token_type"] == "refresh"
        assert decoder.calls[0]["token"] == "refresh-value"

    async def test_threshold_boundary_uses_configured_minutes(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        # Just inside the threshold should rotate.
        exp = _exp_in(Config.ROTATE_THRESHOLD_MINUTES / 60 - 1 / 3600)
        payload = valid_payload(exp=exp)
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        result = await handler.handle(
            RotateTokensCommand(refresh_token="t", device=payload["dev"])
        )
        assert result.refresh_token is not None

    async def test_malformed_exp_skips_rotation(
        self, handler, session_repo, decoder, valid_payload, make_session
    ):
        payload = valid_payload()
        payload["exp"] = "not-a-number"
        await session_repo.add(
            make_session(user_id=payload["sub"], session_id=payload["sid"])
        )
        decoder.payload = payload

        result = await handler.handle(
            RotateTokensCommand(refresh_token="t", device=payload["dev"])
        )
        assert result.refresh_token is None


class TestRotateTokensFailures:
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
                RotateTokensCommand(refresh_token="t", device="Different")
            )

    async def test_revoked_session_cannot_rotate(self, handler, decoder, valid_payload):
        payload = valid_payload()
        decoder.payload = payload

        with pytest.raises(SessionNotFoundError):
            await handler.handle(
                RotateTokensCommand(refresh_token="t", device=payload["dev"])
            )
