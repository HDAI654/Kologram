"""Django settings — Kologram Admin Service (default Django admin panel)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me-admin-service")
DEBUG = os.getenv("APP_ENV", "development") != "production"
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.getenv("DJANGO_ADMIN_DB", str(BASE_DIR / "admin_panel.sqlite3")),
    },
    "auth": {
        "ENGINE": os.getenv("AUTH_DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("AUTH_DB_NAME", "auth"),
        "USER": os.getenv("AUTH_DB_USER", "postgres"),
        "PASSWORD": os.getenv("AUTH_DB_PASSWORD", "postgres"),
        "HOST": os.getenv("AUTH_DB_HOST", "localhost"),
        "PORT": os.getenv("AUTH_DB_PORT", "5432"),
    },
    "market": {
        "ENGINE": os.getenv("MARKET_DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.getenv("MARKET_DB_NAME", "market"),
        "USER": os.getenv("MARKET_DB_USER", "postgres"),
        "PASSWORD": os.getenv("MARKET_DB_PASSWORD", "postgres"),
        "HOST": os.getenv("MARKET_DB_HOST", "localhost"),
        "PORT": os.getenv("MARKET_DB_PORT", "5432"),
    },
}

DATABASE_ROUTERS = ["core.db_router.KologramDatabaseRouter"]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

APP_NAME = os.getenv("APP_NAME", "Kologram")
