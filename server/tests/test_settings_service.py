"""Tests for the settings service.

Each test runs against a fresh in-memory SQLite DB so encryption state and
saved values don't leak between tests.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server import settings_service
from server.db import connection
from server.db.schema import Base


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    """Replace the global engine/session with an in-memory DB for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(connection, "engine", engine)
    monkeypatch.setattr(connection, "SessionLocal", SessionLocal)

    settings_service.lock()
    yield
    settings_service.lock()


def test_set_and_get_plain_setting_roundtrip():
    settings_service.set("ntfy.default_topic", "my-topic")
    assert settings_service.get("ntfy.default_topic") == "my-topic"


def test_get_missing_returns_none():
    assert settings_service.get("ntfy.default_topic") is None


def test_secret_stored_plain_when_no_master_password():
    settings_service.set("telegram.bot_token", "12345:abc")
    assert settings_service.get("telegram.bot_token") == "12345:abc"
    status = settings_service.get_status()
    assert status["has_master_password"] is False
    assert status["encrypted_count"] == 0
    assert status["secret_count"] == 1


def test_init_master_password_encrypts_existing_secrets():
    settings_service.set("telegram.bot_token", "12345:abc")
    settings_service.set("ntfy.default_topic", "my-topic")

    settings_service.init_master_password("hunter2")

    status = settings_service.get_status()
    assert status["has_master_password"] is True
    assert status["is_unlocked"] is True
    assert status["encrypted_count"] == 1  # only the secret got encrypted

    assert settings_service.get("telegram.bot_token") == "12345:abc"
    assert settings_service.get("ntfy.default_topic") == "my-topic"


def test_secrets_inaccessible_when_locked():
    settings_service.init_master_password("hunter2")
    settings_service.set("telegram.bot_token", "12345:abc")
    settings_service.lock()

    with pytest.raises(RuntimeError, match="encrypted"):
        settings_service.get("telegram.bot_token")

    settings_service.unlock("hunter2")
    assert settings_service.get("telegram.bot_token") == "12345:abc"


def test_unlock_with_wrong_password_raises():
    settings_service.init_master_password("hunter2")
    settings_service.lock()
    with pytest.raises(RuntimeError, match="Wrong master password"):
        settings_service.unlock("wrong-password")


def test_change_master_password_reencrypts_secrets():
    settings_service.init_master_password("first-pass")
    settings_service.set("telegram.bot_token", "12345:abc")
    settings_service.set("openweather.api_key", "key-xyz")

    settings_service.change_master_password("first-pass", "second-pass")

    assert settings_service.get("telegram.bot_token") == "12345:abc"

    settings_service.lock()
    settings_service.unlock("second-pass")
    assert settings_service.get("openweather.api_key") == "key-xyz"

    settings_service.lock()
    with pytest.raises(RuntimeError, match="Wrong master password"):
        settings_service.unlock("first-pass")


def test_resolve_prefers_recipe_override():
    settings_service.set("telegram.bot_token", "from-db")
    out = settings_service.resolve(
        "telegram.bot_token",
        recipe_override="from-recipe",
        env_fallback="from-env",
    )
    assert out == "from-recipe"


def test_resolve_falls_back_to_db_then_env():
    settings_service.set("telegram.bot_token", "from-db")
    assert settings_service.resolve("telegram.bot_token", env_fallback="from-env") == "from-db"

    settings_service.delete("telegram.bot_token")
    assert settings_service.resolve("telegram.bot_token", env_fallback="from-env") == "from-env"


def test_resolve_falls_back_to_env_when_locked():
    settings_service.init_master_password("hunter2")
    settings_service.set("telegram.bot_token", "from-db")
    settings_service.lock()
    assert settings_service.resolve("telegram.bot_token", env_fallback="from-env") == "from-env"


def test_list_visible_masks_secrets():
    settings_service.set("telegram.bot_token", "12345:abc")
    settings_service.set("ntfy.default_topic", "my-topic")

    items = settings_service.list_visible()
    by_key = {item["key"]: item for item in items}

    assert by_key["telegram.bot_token"]["is_set"] is True
    assert by_key["telegram.bot_token"]["value"] == "••••••"
    assert by_key["ntfy.default_topic"]["value"] == "my-topic"


def test_unknown_setting_get_def_returns_none():
    assert settings_service.get_def("nonsense.key") is None


def test_init_master_rejects_empty_password():
    with pytest.raises(RuntimeError, match="cannot be empty"):
        settings_service.init_master_password("")


def test_init_master_fails_when_already_set():
    settings_service.init_master_password("first")
    with pytest.raises(RuntimeError, match="already set"):
        settings_service.init_master_password("second")
