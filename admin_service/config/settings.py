import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ===== APP =====

APP_NAME = os.getenv("APP_NAME", "Kologram")
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only-change-me-admin-service")
DEBUG = os.getenv("APP_ENV", "development") != "production"


# ===== HOST / SECURITY =====

ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]


# ===== APPS =====

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core.apps.CoreConfig",
]


# ===== MIDDLEWARE =====

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ===== TEMPLATES =====

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


# ===== WSGI / ASGI =====

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ===== DATABASES =====

DATABASES = {
    "default": dj_database_url.parse(
        os.getenv("ADMIN_DB_URL", "sqlite:///./admin_panel.sqlite3"),
        conn_max_age=600,
    ),
    "auth": dj_database_url.parse(
        os.getenv("AUTH_DB_URL", "postgresql://postgres:postgres@localhost:5432/auth"),
        conn_max_age=600,
    ),
    "market": dj_database_url.parse(
        os.getenv(
            "MARKET_DB_URL", "postgresql://postgres:postgres@localhost:5432/market"
        ),
        conn_max_age=600,
    ),
}

DATABASE_ROUTERS = ["core.db_router.KologramDatabaseRouter"]


# ===== AUTHENTICATION =====

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ===== INTERNATIONALIZATION =====

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ===== STATIC FILES =====

STATIC_URL = "static/"


# ===== DEFAULT PRIMARY KEY =====

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
