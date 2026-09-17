import os
import tempfile
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment — must run before importing src.app / src.conf
# ---------------------------------------------------------------------------

os.environ["APP_NAME"] = "KologramAuth-E2E"
os.environ["APP_ENV"] = "development"
os.environ["RABBITMQ_ENABLED"] = "false"
os.environ["REDIS_ENABLED"] = "false"
os.environ["BLOCKED_EMAILS"] = "blocked@example.com"
os.environ["BLOCKED_EMAIL_DOMAINS"] = "banned.test"

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

_keys_dir = Path(tempfile.mkdtemp(prefix="kologramauth-e2e-keys-"))
_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
(_keys_dir / "private.pem").write_bytes(
    _private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
)
(_keys_dir / "public.pem").write_bytes(
    _private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
)
os.environ["AUTH_PRIVATE_KEY_PATH"] = str(_keys_dir / "private.pem")
os.environ["AUTH_PUBLIC_KEY_PATH"] = str(_keys_dir / "public.pem")

# ---------------------------------------------------------------------------
# Now safe to import the app
# ---------------------------------------------------------------------------

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.presentation import dependencies as deps

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

from src.app import app as _fastapi_app


@pytest.fixture(scope="session")
def app():
    return _fastapi_app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(_fastapi_app)


@pytest.fixture(autouse=True)
def _reset_in_memory_state():
    deps._dev_users._by_id.clear()
    deps._dev_users._by_email.clear()

    session_repo = _fastapi_app.state.session_repository
    session_repo._by_id.clear()
    session_repo._by_user.clear()

    token_repo = _fastapi_app.state.verification_token_repository
    token_repo._store.clear()

    yield


@pytest.fixture
def unique_email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"
