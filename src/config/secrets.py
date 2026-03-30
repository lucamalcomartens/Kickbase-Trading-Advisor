from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values

try:
    import keyring
    from keyring.errors import KeyringError, NoKeyringError
except ImportError:  # pragma: no cover - optional import guard
    keyring = None

    class KeyringError(Exception):
        pass

    class NoKeyringError(KeyringError):
        pass


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SECRET_SERVICE_NAME = "KickAdvisor"
SECRET_KEYS = {
    "KICK_USER": "Kickbase username or email",
    "KICK_PASS": "Kickbase password",
    "GEMINI_API_KEY": "Gemini API key",
    "EMAIL_USER": "Sender email address",
    "EMAIL_PASS": "Sender email app password",
    "FOOTBALL_DATA_API_KEY": "football-data.org API key",
    "API_FOOTBALL_KEY": "API-Football API key",
}
DEFAULT_SECRET_FILES = [
    (PROJECT_ROOT / ".env.local", ".env.local"),
    (PROJECT_ROOT / ".env", ".env"),
]

_loaded = False
_secret_sources: dict[str, str] = {}


def load_runtime_secrets(force_reload: bool = False) -> dict[str, str]:
    """Load secrets into process env without printing values.

    Precedence for missing values is:
    1. Existing process environment
    2. Windows Credential Manager / keyring backend
    3. .env.local
    4. .env
    """

    global _loaded, _secret_sources

    if _loaded and not force_reload:
        return dict(_secret_sources)

    _secret_sources = {}

    for key in SECRET_KEYS:
        if _has_secret_value(os.getenv(key)):
            _secret_sources[key] = "environment"

    for key in SECRET_KEYS:
        if key in _secret_sources:
            continue
        secret_value = _read_secret_from_keyring(key)
        if _has_secret_value(secret_value):
            os.environ[key] = secret_value
            _secret_sources[key] = "credential_manager"

    for file_path, source_name in DEFAULT_SECRET_FILES:
        if not file_path.exists():
            continue
        for key, raw_value in dotenv_values(file_path).items():
            if key not in SECRET_KEYS or key in _secret_sources or not _has_secret_value(raw_value):
                continue
            os.environ[key] = str(raw_value)
            _secret_sources[key] = source_name

    _loaded = True
    return dict(_secret_sources)


def get_secret(secret_key: str, default: str | None = None) -> str | None:
    load_runtime_secrets()
    value = os.getenv(secret_key)
    return value if _has_secret_value(value) else default


def validate_required_secrets(required_keys: list[str] | tuple[str, ...]) -> list[str]:
    load_runtime_secrets()
    return [key for key in required_keys if not _has_secret_value(os.getenv(key))]


def get_secret_status(secret_keys: list[str] | tuple[str, ...] | None = None) -> list[dict[str, str | bool | None]]:
    load_runtime_secrets()
    keys_to_check = list(secret_keys or SECRET_KEYS.keys())
    return [
        {
            "key": key,
            "configured": _has_secret_value(os.getenv(key)),
            "source": _secret_sources.get(key),
            "description": SECRET_KEYS.get(key, ""),
        }
        for key in keys_to_check
    ]


def set_secret_in_keyring(secret_key: str, secret_value: str) -> None:
    if secret_key not in SECRET_KEYS:
        raise ValueError(f"Unsupported secret key: {secret_key}")
    if not _has_keyring_backend():
        raise RuntimeError("No supported keyring backend available. Install keyring and configure a local backend.")
    keyring.set_password(SECRET_SERVICE_NAME, secret_key, secret_value)
    os.environ[secret_key] = secret_value
    _secret_sources[secret_key] = "credential_manager"


def delete_secret_from_keyring(secret_key: str) -> bool:
    if secret_key not in SECRET_KEYS:
        raise ValueError(f"Unsupported secret key: {secret_key}")
    if not _has_keyring_backend():
        raise RuntimeError("No supported keyring backend available. Install keyring and configure a local backend.")

    try:
        keyring.delete_password(SECRET_SERVICE_NAME, secret_key)
        deleted = True
    except KeyringError:
        deleted = False

    if secret_key in os.environ:
        os.environ.pop(secret_key)
    _secret_sources.pop(secret_key, None)
    return deleted


def mask_secret(secret_value: str | None) -> str:
    if not _has_secret_value(secret_value):
        return "<missing>"
    if len(secret_value) <= 4:
        return "*" * len(secret_value)
    return f"{secret_value[:2]}{'*' * max(4, len(secret_value) - 4)}{secret_value[-2:]}"


def _has_secret_value(secret_value) -> bool:
    return secret_value is not None and str(secret_value).strip() != ""


def _read_secret_from_keyring(secret_key: str) -> str | None:
    if not _has_keyring_backend():
        return None
    try:
        return keyring.get_password(SECRET_SERVICE_NAME, secret_key)
    except (KeyringError, RuntimeError):
        return None


def _has_keyring_backend() -> bool:
    if keyring is None:
        return False
    try:
        backend = keyring.get_keyring()
    except Exception:
        return False
    return backend is not None and backend.__class__.__name__.lower() != "failkeyring"