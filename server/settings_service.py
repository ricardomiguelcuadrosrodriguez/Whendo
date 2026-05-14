"""Settings service: persistent configuration with optional master-password
encryption for secrets.

Storage model
-------------
- Non-secret settings (server URLs, default chat IDs, etc.) are stored as
  plain text in the `app_setting` table.
- Secret settings (API keys, tokens, passwords) are stored as plain text
  when no master password has been set, or as Fernet tokens once one has.
- The master password itself is never stored. We persist its PBKDF2 salt
  and a small verifier ciphertext so we can validate a given password on
  unlock.

Runtime model
-------------
A single `_master` slot in process memory holds the derived Fernet key after
an unlock. Locking clears it. Without a master password set, secrets are
plain text and the slot stays empty.

Catalog
-------
`SETTINGS_CATALOG` declares every user-configurable setting: its key,
human-readable label, category, secret flag, optional default, optional
description and placeholder. The frontend reads this to auto-build forms.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from server.db.connection import get_session
from server.db.schema import AppMeta, AppSetting

_META_SALT = "master.salt"
_META_VERIFIER = "master.verifier"
_META_KDF_ITERS = "master.kdf_iters"
_DEFAULT_KDF_ITERS = 600_000
_VERIFIER_PLAINTEXT = b"whendo-master-ok"


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SettingDef:
    key: str
    label: str
    category: str  # "notifications" | "data_sources" | "ai"
    is_secret: bool = False
    default: str | None = None
    description: str | None = None
    placeholder: str | None = None


SETTINGS_CATALOG: tuple[SettingDef, ...] = (
    # Notifications -----------------------------------------------------------
    SettingDef("telegram.bot_token", "Telegram bot token", "notifications",
               is_secret=True, placeholder="123456:ABC-DEF…",
               description="Talk to @BotFather to create a bot and copy its token here."),
    SettingDef("telegram.default_chat_id", "Telegram chat ID", "notifications",
               placeholder="123456789",
               description="The chat where messages will be sent. Send a message to your bot then check https://api.telegram.org/bot<token>/getUpdates."),
    SettingDef("ntfy.server", "ntfy server URL", "notifications",
               default="https://ntfy.sh", placeholder="https://ntfy.sh"),
    SettingDef("ntfy.default_topic", "ntfy topic", "notifications",
               placeholder="my-whendo-topic",
               description="A long, unguessable string acts as the password."),
    SettingDef("smtp.host", "SMTP host", "notifications", placeholder="smtp.gmail.com"),
    SettingDef("smtp.port", "SMTP port", "notifications", default="587", placeholder="587"),
    SettingDef("smtp.user", "SMTP user", "notifications", placeholder="you@example.com"),
    SettingDef("smtp.pass", "SMTP password", "notifications", is_secret=True),
    SettingDef("smtp.from", "SMTP from address", "notifications", placeholder="whendo@example.com"),
    SettingDef("discord.webhook_url", "Discord webhook URL", "notifications",
               is_secret=True, placeholder="https://discord.com/api/webhooks/…"),
    SettingDef("twilio.account_sid", "Twilio account SID", "notifications", is_secret=True),
    SettingDef("twilio.auth_token", "Twilio auth token", "notifications", is_secret=True),
    SettingDef("twilio.whatsapp_from", "Twilio WhatsApp number", "notifications",
               placeholder="whatsapp:+14155238886"),
    # Data sources ------------------------------------------------------------
    SettingDef("openweather.api_key", "OpenWeatherMap API key", "data_sources",
               is_secret=True,
               description="Free tier is plenty. Sign up at openweathermap.org/api."),
    SettingDef("spotify.client_id", "Spotify client ID", "data_sources", is_secret=True),
    SettingDef("spotify.client_secret", "Spotify client secret", "data_sources", is_secret=True),
    SettingDef("youtube.api_key", "YouTube Data API key", "data_sources", is_secret=True),
    SettingDef("github.token", "GitHub personal access token", "data_sources",
               is_secret=True,
               description="Optional. Public repo releases work without a token, but you get higher rate limits with one."),
    # AI ----------------------------------------------------------------------
    SettingDef("llm.provider", "LLM provider", "ai",
               default="anthropic", placeholder="anthropic | openai | ollama"),
    SettingDef("llm.model", "LLM model", "ai", default="claude-haiku-4-5-20251001"),
    SettingDef("llm.api_key", "LLM API key", "ai", is_secret=True),
    SettingDef("llm.ollama_host", "Ollama host (if using Ollama)", "ai",
               default="http://localhost:11434"),
)

_CATALOG_BY_KEY: dict[str, SettingDef] = {s.key: s for s in SETTINGS_CATALOG}


def catalog() -> tuple[SettingDef, ...]:
    return SETTINGS_CATALOG


def get_def(key: str) -> SettingDef | None:
    return _CATALOG_BY_KEY.get(key)


# ---------------------------------------------------------------------------
# Master password / encryption state
# ---------------------------------------------------------------------------

class _MasterState:
    """In-memory key slot. Cleared on lock or restart."""

    def __init__(self) -> None:
        self._fernet: Fernet | None = None

    def set(self, fernet: Fernet) -> None:
        self._fernet = fernet

    def clear(self) -> None:
        self._fernet = None

    @property
    def is_unlocked(self) -> bool:
        return self._fernet is not None

    @property
    def fernet(self) -> Fernet | None:
        return self._fernet


_master = _MasterState()


def _derive_key(password: str, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def _meta_get(key: str) -> str | None:
    with get_session() as session:
        row = session.get(AppMeta, key)
        return row.value if row else None


def _meta_set(key: str, value: str) -> None:
    with get_session() as session:
        row = session.get(AppMeta, key)
        if row:
            row.value = value
            row.updated_at = datetime.now(timezone.utc)
        else:
            session.add(AppMeta(key=key, value=value, updated_at=datetime.now(timezone.utc)))


def has_master_password() -> bool:
    return _meta_get(_META_SALT) is not None and _meta_get(_META_VERIFIER) is not None


def is_unlocked() -> bool:
    return _master.is_unlocked


def init_master_password(password: str) -> None:
    """Set the master password for the first time. Fails if already set."""
    if has_master_password():
        raise RuntimeError("A master password is already set. Use change_master_password() instead.")
    if not password:
        raise RuntimeError("Master password cannot be empty.")

    salt = os.urandom(16)
    iterations = _DEFAULT_KDF_ITERS
    key = _derive_key(password, salt, iterations)
    fernet = Fernet(key)
    verifier = fernet.encrypt(_VERIFIER_PLAINTEXT).decode("ascii")

    _meta_set(_META_SALT, base64.b64encode(salt).decode("ascii"))
    _meta_set(_META_VERIFIER, verifier)
    _meta_set(_META_KDF_ITERS, str(iterations))

    _master.set(fernet)
    _encrypt_existing_secrets(fernet)


def unlock(password: str) -> None:
    """Unlock the secrets store with the given master password."""
    salt_b64 = _meta_get(_META_SALT)
    verifier = _meta_get(_META_VERIFIER)
    iterations_str = _meta_get(_META_KDF_ITERS)
    if not salt_b64 or not verifier or not iterations_str:
        raise RuntimeError("No master password has been set.")

    salt = base64.b64decode(salt_b64)
    iterations = int(iterations_str)
    key = _derive_key(password, salt, iterations)
    fernet = Fernet(key)

    try:
        if fernet.decrypt(verifier.encode("ascii")) != _VERIFIER_PLAINTEXT:
            raise RuntimeError("Wrong master password.")
    except InvalidToken as e:
        raise RuntimeError("Wrong master password.") from e

    _master.set(fernet)


def lock() -> None:
    _master.clear()


def change_master_password(old_password: str, new_password: str) -> None:
    """Change the master password and re-encrypt all secrets."""
    unlock(old_password)  # validates old password and sets _master
    if not new_password:
        raise RuntimeError("New master password cannot be empty.")

    salt = os.urandom(16)
    iterations = _DEFAULT_KDF_ITERS
    new_key = _derive_key(new_password, salt, iterations)
    new_fernet = Fernet(new_key)

    old_fernet = _master.fernet
    assert old_fernet is not None  # for type-checker; unlock() ensures this

    with get_session() as session:
        rows = session.query(AppSetting).filter(AppSetting.is_encrypted == True).all()  # noqa: E712
        for row in rows:
            plain = old_fernet.decrypt(row.value.encode("ascii"))
            row.value = new_fernet.encrypt(plain).decode("ascii")
            row.updated_at = datetime.now(timezone.utc)

    _meta_set(_META_SALT, base64.b64encode(salt).decode("ascii"))
    _meta_set(_META_VERIFIER, new_fernet.encrypt(_VERIFIER_PLAINTEXT).decode("ascii"))
    _meta_set(_META_KDF_ITERS, str(iterations))
    _master.set(new_fernet)


def _encrypt_existing_secrets(fernet: Fernet) -> None:
    """Called when a master password is set for the first time: take all
    existing plain-text secrets and encrypt them in place."""
    with get_session() as session:
        rows = session.query(AppSetting).filter(
            AppSetting.is_secret == True,  # noqa: E712
            AppSetting.is_encrypted == False,  # noqa: E712
        ).all()
        for row in rows:
            row.value = fernet.encrypt(row.value.encode("utf-8")).decode("ascii")
            row.is_encrypted = True
            row.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Setting get / set
# ---------------------------------------------------------------------------

def get(key: str) -> str | None:
    """Return the plain-text value of a setting, or None if not set.

    Raises:
        RuntimeError if the value is encrypted and the store is locked.
    """
    with get_session() as session:
        row = session.get(AppSetting, key)
        if row is None:
            return None
        if row.is_encrypted:
            if not _master.is_unlocked:
                raise RuntimeError(
                    f"Setting '{key}' is encrypted; unlock with the master password first."
                )
            assert _master.fernet is not None
            return _master.fernet.decrypt(row.value.encode("ascii")).decode("utf-8")
        return row.value


def set(key: str, value: str) -> None:  # noqa: A001 — matches conventional service API
    definition = _CATALOG_BY_KEY.get(key)
    is_secret = bool(definition and definition.is_secret)
    should_encrypt = is_secret and _master.is_unlocked

    if should_encrypt:
        assert _master.fernet is not None
        stored_value = _master.fernet.encrypt(value.encode("utf-8")).decode("ascii")
    else:
        stored_value = value

    with get_session() as session:
        row = session.get(AppSetting, key)
        if row:
            row.value = stored_value
            row.is_secret = is_secret
            row.is_encrypted = should_encrypt
            row.updated_at = datetime.now(timezone.utc)
        else:
            session.add(AppSetting(
                key=key,
                value=stored_value,
                is_secret=is_secret,
                is_encrypted=should_encrypt,
                updated_at=datetime.now(timezone.utc),
            ))


def delete(key: str) -> None:
    with get_session() as session:
        row = session.get(AppSetting, key)
        if row:
            session.delete(row)


def is_set(key: str) -> bool:
    with get_session() as session:
        return session.get(AppSetting, key) is not None


def list_visible() -> list[dict]:
    """Return all catalog entries with their status. Secrets are masked."""
    with get_session() as session:
        rows = {row.key: row for row in session.query(AppSetting).all()}

    out: list[dict] = []
    for definition in SETTINGS_CATALOG:
        row = rows.get(definition.key)
        is_set_ = row is not None
        value: str | None
        if not is_set_:
            value = None
        elif definition.is_secret:
            value = "••••••" if row.value else ""
        elif row.is_encrypted and not _master.is_unlocked:
            value = None
        elif row.is_encrypted:
            assert _master.fernet is not None
            value = _master.fernet.decrypt(row.value.encode("ascii")).decode("utf-8")
        else:
            value = row.value
        out.append({
            "key": definition.key,
            "label": definition.label,
            "category": definition.category,
            "is_secret": definition.is_secret,
            "default": definition.default,
            "description": definition.description,
            "placeholder": definition.placeholder,
            "is_set": is_set_,
            "value": value,
        })
    return out


def get_status() -> dict:
    """Lock / setup status for the UI."""
    secret_count = 0
    encrypted_count = 0
    with get_session() as session:
        secret_count = session.query(AppSetting).filter(
            AppSetting.is_secret == True  # noqa: E712
        ).count()
        encrypted_count = session.query(AppSetting).filter(
            AppSetting.is_encrypted == True  # noqa: E712
        ).count()
    return {
        "has_master_password": has_master_password(),
        "is_unlocked": _master.is_unlocked,
        "secret_count": secret_count,
        "encrypted_count": encrypted_count,
    }


# ---------------------------------------------------------------------------
# Runtime resolver — used by sources / actions
# ---------------------------------------------------------------------------

def resolve(
    key: str,
    *,
    recipe_override: str | None = None,
    env_fallback: str | None = None,
) -> str | None:
    """Resolve a setting at runtime.

    Priority:
        1. value passed in the recipe YAML (recipe_override)
        2. value stored in the DB (settings_service.get)
        3. value from .env (env_fallback)
    """
    if recipe_override:
        return recipe_override
    try:
        db_value = get(key)
        if db_value:
            return db_value
    except RuntimeError:
        # Encrypted but locked — fall through to env.
        pass
    if env_fallback:
        return env_fallback
    return None


__all__ = [
    "SETTINGS_CATALOG",
    "SettingDef",
    "catalog",
    "change_master_password",
    "delete",
    "get",
    "get_def",
    "get_status",
    "has_master_password",
    "init_master_password",
    "is_set",
    "is_unlocked",
    "list_visible",
    "lock",
    "resolve",
    "set",
    "unlock",
]
