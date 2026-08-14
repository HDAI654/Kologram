"""Environment-driven configuration for notification-dispatcher."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_SERVICE_DIR = Path(__file__).resolve().parent.parent
_env = _SERVICE_DIR / ".env"
if _env.exists():
    load_dotenv(_env)


def _bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "on")


class Config:
    APP_NAME: str = os.getenv("APP_NAME", "notification-dispatcher")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_ENABLED: bool = _bool("RABBITMQ_ENABLED", False)
    # Comma-separated topic exchanges to bind (match producer services).
    RABBITMQ_EXCHANGES: str = os.getenv(
        "RABBITMQ_EXCHANGES", "auth.events,listing.events"
    )
    RABBITMQ_QUEUE: str = os.getenv("RABBITMQ_QUEUE", "notification.dispatcher")
    RABBITMQ_PREFETCH: int = int(os.getenv("RABBITMQ_PREFETCH", "10"))
    RABBITMQ_DLX: str = os.getenv("RABBITMQ_DLX", "notification.dlx")
    RABBITMQ_DLQ: str = os.getenv("RABBITMQ_DLQ", "notification.dispatcher.dlq")

    # Routing keys / event types consumed (comma-separated). Empty = bind "#".
    RABBITMQ_ROUTING_KEYS: str = os.getenv(
        "RABBITMQ_ROUTING_KEYS",
        "AccountDeleted,UserLoggedIn,UserLoggedOut,UserRegistered,"
        "VerificationTokenCreated,CategoryCreated,ListingCreated,"
        "ListingDeleted,ListingPublished,ListingStatusChanged,ListingUpdated",
    )

    EMAIL_ENABLED: bool = _bool("EMAIL_ENABLED", False)
    EMAIL_PROVIDER: str = os.getenv("EMAIL_PROVIDER", "console")  # console|smtp
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = _bool("SMTP_USE_TLS", False)
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@kologram.local")
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@kologram.local")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@kologram.local")

    # SQLite path for idempotency records (use :memory: only in pure unit tests).
    IDEMPOTENCY_DB_URL: str = os.getenv(
        "IDEMPOTENCY_DB_URL",
        f"sqlite+aiosqlite:///{_SERVICE_DIR / 'data' / 'idempotency.db'}",
    )
    IDEMPOTENCY_ENABLED: bool = _bool("IDEMPOTENCY_ENABLED", True)

    @classmethod
    def exchanges(cls) -> list[str]:
        return [x.strip() for x in cls.RABBITMQ_EXCHANGES.split(",") if x.strip()]

    @classmethod
    def routing_keys(cls) -> list[str]:
        return [k.strip() for k in cls.RABBITMQ_ROUTING_KEYS.split(",") if k.strip()]
