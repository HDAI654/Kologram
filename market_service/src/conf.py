"""Market service configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_SERVICE_DIR = Path(__file__).resolve().parent.parent
_env = _SERVICE_DIR / ".env"
if os.getenv("APP_NAME") is None and _env.exists():
    load_dotenv(_env)


class Config:
    APP_NAME: str = os.getenv("APP_NAME", "Kologram")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )

    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    RABBITMQ_ENABLED: bool = os.getenv("RABBITMQ_ENABLED", "false").lower() in (
        "1",
        "true",
        "yes",
    )
    RABBITMQ_EXCHANGE: str = os.getenv("RABBITMQ_EXCHANGE", "listing.events")
