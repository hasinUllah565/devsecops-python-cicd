"""Application configuration, driven by environment variables."""
import os
import secrets
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

INSTANCE_DIR = BASE_DIR / "instance"


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a boolean flag from the environment."""
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _default_database_uri() -> str:
    """Return the SQLite URI used when DATABASE_URL is not provided."""
    INSTANCE_DIR.mkdir(exist_ok=True)
    return f"sqlite:///{INSTANCE_DIR / 'app.db'}"


class Config:
    """Base configuration shared by every environment."""

    # No secret is ever hardcoded. When SECRET_KEY is unset a random key is
    # generated at start-up (sessions then reset on restart), so set it in .env.
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or _default_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session and cookie hardening
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE", False)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # CSRF protection (Flask-WTF)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    MAX_CONTENT_LENGTH = 1024 * 1024  # 1 MB request limit


class TestingConfig(Config):
    """Configuration used by the pytest suite."""

    TESTING = True
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
