"""Environment-driven configuration for notification_dispatcher."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_SERVICE_DIR = Path(__file__).resolve().parent.parent
_env = _SERVICE_DIR / ".env"
if _env.exists():
    load_dotenv(_env)


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


class Config:
    APP_NAME: str = os.getenv("APP_NAME", "notification_dispatcher")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_EXCHANGES: str = os.getenv(
        "RABBITMQ_EXCHANGES",
        "auth.events,listing.events,chat.events",
    )
    RABBITMQ_QUEUE: str = os.getenv("RABBITMQ_QUEUE", "notification.dispatcher")
    RABBITMQ_PREFETCH: int = int(os.getenv("RABBITMQ_PREFETCH", "10"))

    # EMAIL_ENABLED: 1/true/TRUE/yes → SMTP; otherwise console (log only).
    EMAIL_ENABLED: bool = _truthy("EMAIL_ENABLED", False)
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@kologram.local")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = _truthy("SMTP_USE_TLS", True)
    SMTP_USE_SSL: bool = _truthy("SMTP_USE_SSL", False)

    EMAIL_MAX_ATTEMPTS: int = int(os.getenv("EMAIL_MAX_ATTEMPTS", "3"))

    IDEMPOTENCY_DB_PATH: str = os.getenv(
        "IDEMPOTENCY_DB_PATH",
        str(_SERVICE_DIR / "data" / "idempotency.sqlite3"),
    )

    @classmethod
    def exchanges(cls) -> list[str]:
        return [x.strip() for x in cls.RABBITMQ_EXCHANGES.split(",") if x.strip()]
