import uuid
import pytest
from tests.e2e.helpers import (
    auth_header,
    forget_password,
    latest_verification_token,
    login,
    request_verification,
    reset_password,
    signup,
)

AUTH = "/api/v1/auth"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class TestHealth:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


class TestSendVerification:
    def test_valid_email_returns_204(self, client, unique_email):
        response = client.post(f"{AUTH}/verification", json={"email": unique_email})
        assert response.status_code == 204

    def test_blocked_email_returns_403(self, client):
        response = client.post(
            f"{AUTH}/verification", json={"email": "blocked@example.com"}
        )
        assert response.status_code == 403

    def test_blocked_domain_returns_403(self, client):
        response = client.post(
            f"{AUTH}/verification", json={"email": "anyone@banned.test"}
        )
        assert response.status_code == 403

    def test_invalid_email_returns_422(self, client):
        response = client.post(f"{AUTH}/verification", json={"email": "not-an-email"})
        assert response.status_code == 422

    def test_too_short_email_returns_422(self, client):
        response = client.post(f"{AUTH}/verification", json={"email": "a@b"})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------


class TestSignup:
    def test_signup_with_verification_token_issues_tokens(
        self, client, app, unique_email
    ):
        request_verification(client, unique_email)
        token = latest_verification_token(app, unique_email)

        response = client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": token,
                "password": "password1",
                "device": "iPhone 15",
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["access_token"]
        assert body["refresh_token"]

    def test_signup_consumes_verification_token(self, client, app, unique_email):
        request_verification(client, unique_email)
        token = latest_verification_token(app, unique_email)

        client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": token,
                "password": "password1",
                "device": "iPhone 15",
            },
        )

        # Second use of the same token must fail.
        response = client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": token,
                "password": "password2",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 400

    def test_signup_with_unknown_token_returns_400(self, client):
        response = client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": str(uuid.uuid4()),
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 400

    def test_signup_with_weak_password_returns_422(self, client, app, unique_email):
        request_verification(client, unique_email)
        token = latest_verification_token(app, unique_email)

        response = client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": token,
                "password": "short",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 422

    def test_signup_with_malformed_token_returns_422(self, client):
        response = client.post(
            f"{AUTH}/signup",
            json={
                "verify_token": "not-a-uuid",
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLogin:
    def test_login_after_signup_succeeds(self, client, app, unique_email):
        signup(client, app, email=unique_email)

        access, refresh = login(client, email=unique_email)

        assert access
        assert refresh

    def test_login_with_wrong_password_returns_401(self, client, app, unique_email):
        signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "wrongpass1",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_login_with_unknown_email_returns_401(self, client):
        response = client.post(
            f"{AUTH}/login",
            json={
                "email": "ghost@example.com",
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 401

    def test_login_with_invalid_email_returns_422(self, client):
        response = client.post(
            f"{AUTH}/login",
            json={
                "email": "not-an-email",
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestLogout:
    def test_logout_with_valid_token_returns_204(self, client, app, unique_email):
        access, _ = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/logout",
            json={"device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert response.status_code == 204

    def test_logout_without_auth_header_returns_401(self, client):
        response = client.post(f"{AUTH}/logout", json={"device": "iPhone 15"})
        assert response.status_code == 401

    def test_logout_with_wrong_device_returns_403(self, client, app, unique_email):
        access, _ = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/logout",
            json={"device": "DifferentDevice"},
            headers=auth_header(access),
        )
        assert response.status_code == 403

    def test_logout_twice_returns_401(self, client, app, unique_email):
        access, _ = signup(client, app, email=unique_email)

        first = client.post(
            f"{AUTH}/logout",
            json={"device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert first.status_code == 204

        second = client.post(
            f"{AUTH}/logout",
            json={"device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert second.status_code == 401


# ---------------------------------------------------------------------------
# Token rotation
# ---------------------------------------------------------------------------


class TestRotateTokens:
    def test_refresh_issues_new_access_token(self, client, app, unique_email):
        _, refresh = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/token/refresh",
            json={"refresh_token": refresh, "device": "iPhone 15"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        # Far from expiry — no refresh rotation.
        assert body["refresh_token"] is None

    def test_refresh_with_revoked_session_returns_401(self, client, app, unique_email):
        access, refresh = signup(client, app, email=unique_email)
        client.post(
            f"{AUTH}/logout",
            json={"device": "iPhone 15"},
            headers=auth_header(access),
        )

        response = client.post(
            f"{AUTH}/token/refresh",
            json={"refresh_token": refresh, "device": "iPhone 15"},
        )
        assert response.status_code == 401

    def test_refresh_with_wrong_device_returns_403(self, client, app, unique_email):
        _, refresh = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/token/refresh",
            json={"refresh_token": refresh, "device": "DifferentDevice"},
        )
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Set password
# ---------------------------------------------------------------------------


class TestSetPassword:
    def test_set_password_changes_login_credentials(self, client, app, unique_email):
        access, _ = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/password",
            json={"new_password": "newpass99", "device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert response.status_code == 204

        # Old password no longer works.
        old = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert old.status_code == 401

        # New password works.
        new = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "newpass99",
                "device": "iPhone 15",
            },
        )
        assert new.status_code == 200

    def test_set_password_without_auth_returns_401(self, client):
        response = client.post(
            f"{AUTH}/password",
            json={"new_password": "newpass99", "device": "iPhone 15"},
        )
        assert response.status_code == 401

    def test_set_password_with_weak_password_returns_422(
        self, client, app, unique_email
    ):
        access, _ = signup(client, app, email=unique_email)

        response = client.post(
            f"{AUTH}/password",
            json={"new_password": "short", "device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Forget + reset password
# ---------------------------------------------------------------------------


class TestPasswordReset:
    def test_full_forget_and_reset_flow(self, client, app, unique_email):
        signup(client, app, email=unique_email)

        reset_password(client, app, email=unique_email, new_password="newpass99")

        response = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "newpass99",
                "device": "iPhone 15",
            },
        )
        assert response.status_code == 200

    def test_forget_unknown_email_is_silent_204(self, client):
        response = client.post(
            f"{AUTH}/password/forgot", json={"email": "ghost@example.com"}
        )
        # Anti-enumeration: same response whether or not the email exists.
        assert response.status_code == 204

    def test_reset_with_unknown_token_returns_400(self, client):
        response = client.post(
            f"{AUTH}/password/reset",
            json={
                "verify_token": str(uuid.uuid4()),
                "new_password": "newpass99",
            },
        )
        assert response.status_code == 400

    def test_reset_with_weak_password_returns_422(self, client, app, unique_email):
        signup(client, app, email=unique_email)
        forget_password(client, unique_email)
        token = latest_verification_token(app, unique_email, "forget_pass_verify")

        response = client.post(
            f"{AUTH}/password/reset",
            json={"verify_token": token, "new_password": "short"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Revoke sessions
# ---------------------------------------------------------------------------


class TestRevokeSession:
    def test_revoke_own_session_succeeds(self, client, app, unique_email):
        access_a, _ = signup(client, app, email=unique_email, device="iPhone 15")
        # Second login to create another session.
        access_b, _ = login(client, email=unique_email, device="Pixel 8")

        # Find session id of session B from its token.
        from src.presentation.dependencies import get_token_decoder

        decoder = get_token_decoder()
        encoder = get_token_encoder() if False else None  # noqa: F841
        from src.presentation.dependencies import get_token_encoder

        encoder = get_token_encoder()
        payload_b = decoder.decode_and_validate(
            field_type_map=encoder.FIELD_TYPE_MAP,
            token=access_b,
            expected_token_type="access",
        )

        response = client.post(
            f"{AUTH}/sessions/revoke",
            json={"session_id": payload_b["sid"], "device": "iPhone 15"},
            headers=auth_header(access_a),
        )
        assert response.status_code == 204

    def test_revoke_cross_user_session_returns_403(self, client, app):
        access_a, _ = signup(client, app, email=f"a-{uuid.uuid4().hex[:6]}@example.com")
        access_b, _ = signup(client, app, email=f"b-{uuid.uuid4().hex[:6]}@example.com")

        from src.presentation.dependencies import get_token_decoder, get_token_encoder

        decoder = get_token_decoder()
        encoder = get_token_encoder()
        payload_b = decoder.decode_and_validate(
            field_type_map=encoder.FIELD_TYPE_MAP,
            token=access_b,
            expected_token_type="access",
        )

        response = client.post(
            f"{AUTH}/sessions/revoke",
            json={"session_id": payload_b["sid"], "device": "iPhone 15"},
            headers=auth_header(access_a),
        )
        assert response.status_code == 403

    def test_revoke_without_auth_returns_401(self, client):
        response = client.post(
            f"{AUTH}/sessions/revoke",
            json={"session_id": str(uuid.uuid4()), "device": "iPhone 15"},
        )
        assert response.status_code == 401


class TestRevokeAllOther:
    def test_revoke_others_keeps_current_session(self, client, app, unique_email):
        access_a, _ = signup(client, app, email=unique_email, device="iPhone 15")
        login(client, email=unique_email, device="Pixel 8")

        response = client.post(
            f"{AUTH}/sessions/revoke-others",
            json={"device": "iPhone 15"},
            headers=auth_header(access_a),
        )
        assert response.status_code == 204

        # Current session still usable — rotate to confirm.
        from src.presentation.dependencies import get_token_encoder

        # Refresh tokens from session A cannot be retrieved directly here, so
        # sanity check the current access token by performing another authenticated call.
        followup = client.post(
            f"{AUTH}/sessions/revoke-others",
            json={"device": "iPhone 15"},
            headers=auth_header(access_a),
        )
        assert followup.status_code == 204


# ---------------------------------------------------------------------------
# Delete account
# ---------------------------------------------------------------------------


class TestDeleteAccount:
    def test_delete_account_prevents_future_login(self, client, app, unique_email):
        access, _ = signup(client, app, email=unique_email)

        response = client.request(
            "DELETE",
            f"{AUTH}/account",
            json={"device": "iPhone 15"},
            headers=auth_header(access),
        )
        assert response.status_code == 204

        # Login now fails with the same generic 401.
        login_response = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert login_response.status_code == 401

    def test_delete_account_without_auth_returns_401(self, client):
        response = client.request(
            "DELETE", f"{AUTH}/account", json={"device": "iPhone 15"}
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Full lifecycle
# ---------------------------------------------------------------------------


class TestFullLifecycle:
    def test_signup_login_rotate_set_password_logout(self, client, app, unique_email):
        # 1. Signup.
        access, refresh = signup(client, app, email=unique_email)
        assert access and refresh

        # 2. Rotate.
        rotated = client.post(
            f"{AUTH}/token/refresh",
            json={"refresh_token": refresh, "device": "iPhone 15"},
        )
        assert rotated.status_code == 200
        new_access = rotated.json()["access_token"]

        # 3. Change password via authenticated endpoint.
        changed = client.post(
            f"{AUTH}/password",
            json={"new_password": "newpass99", "device": "iPhone 15"},
            headers=auth_header(new_access),
        )
        assert changed.status_code == 204

        # 4. Old access token still valid (sessions untouched), but old
        # password no longer works — confirms the update took effect.
        old_login = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "password1",
                "device": "iPhone 15",
            },
        )
        assert old_login.status_code == 401

        new_login = client.post(
            f"{AUTH}/login",
            json={
                "email": unique_email,
                "password": "newpass99",
                "device": "iPhone 15",
            },
        )
        assert new_login.status_code == 200

        # 5. Logout the new session.
        logout_access = new_login.json()["access_token"]
        logout = client.post(
            f"{AUTH}/logout",
            json={"device": "iPhone 15"},
            headers=auth_header(logout_access),
        )
        assert logout.status_code == 204
