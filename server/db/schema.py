"""Schema definitions for whendo.

Two kinds of models live here:
- Pydantic models (Recipe, etc.) — used to validate YAML and API payloads.
- SQLAlchemy models (Run, SourceState) — persisted in SQLite.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ---------------------------------------------------------------------------
# Pydantic models — for recipe YAML validation
# ---------------------------------------------------------------------------

class WhenBlock(BaseModel):
    """When should we check? (the trigger).

    Exactly one of `every`, `webhook`, or `on_startup` must be set.
    """

    every: str | None = None
    """A schedule expression. Supported forms:
       - 'day at HH:MM'                 → daily at that local time
       - 'weekday at HH:MM'             → e.g. 'monday at 9am'
       - 'N minutes' | 'N hours' | 'N days'
       - any valid cron expression: '0 7 * * *'
    """
    webhook: str | None = None
    """A path that fires this recipe when POST'd to /webhooks/<path>."""
    on_startup: bool = False
    """Run once when the server starts."""

    model_config = {"extra": "forbid"}


class IfBlock(BaseModel):
    """Optional source + condition. Exactly one source key must be set."""

    weather: dict[str, Any] | None = None
    rss: dict[str, Any] | None = None
    github_releases: dict[str, Any] | None = None
    spotify_new_release: dict[str, Any] | None = None
    web_scrape: dict[str, Any] | None = None
    http_get: dict[str, Any] | None = None

    model_config = {"extra": "allow"}


class ThenBlock(BaseModel):
    """The action. Exactly one action key must be set."""

    notify_telegram: dict[str, Any] | None = None
    notify_ntfy: dict[str, Any] | None = None
    notify_email: dict[str, Any] | None = None
    notify_discord: dict[str, Any] | None = None
    notify_whatsapp: dict[str, Any] | None = None
    webhook_post: dict[str, Any] | None = None
    llm_summarize_and_notify: dict[str, Any] | None = None
    run_shell: dict[str, Any] | None = None

    model_config = {"extra": "allow"}


class Recipe(BaseModel):
    """A complete recipe loaded from a YAML file."""

    name: str = Field(..., min_length=1, description="Human-readable name")
    description: str | None = None
    enabled: bool = True
    when: WhenBlock
    if_: IfBlock | None = Field(default=None, alias="if")
    then: ThenBlock

    model_config = {"populate_by_name": True}

    @property
    def source_name(self) -> str | None:
        """Returns the active source key, e.g. 'weather'."""
        if not self.if_:
            return None
        for k, v in self.if_.model_dump(exclude_none=True).items():
            return k
        return None

    @property
    def action_name(self) -> str:
        """Returns the active action key, e.g. 'notify_telegram'."""
        for k, v in self.then.model_dump(exclude_none=True).items():
            return k
        raise ValueError(f"Recipe '{self.name}' has no action configured")


# ---------------------------------------------------------------------------
# SQLAlchemy models — for persistence
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class Run(Base):
    """One execution of a recipe."""

    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_name: Mapped[str] = mapped_column(String(255), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20))  # success|failed|skipped|running
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class SourceState(Base):
    """Per-recipe state for sources that need memory (e.g. 'last RSS item seen')."""

    __tablename__ = "source_state"

    recipe_name: Mapped[str] = mapped_column(String(255), primary_key=True)
    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[dict] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class AppSetting(Base):
    """One configurable setting, e.g. telegram.bot_token.

    `value` holds either plain text (non-secrets, or secrets when no master
    password has been set) or a Fernet token string (secrets after a master
    password is in place). `is_encrypted` lets the service decide which path.
    """

    __tablename__ = "app_setting"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    is_secret: Mapped[bool] = mapped_column()
    is_encrypted: Mapped[bool] = mapped_column()
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class AppMeta(Base):
    """Single-row table for app-wide metadata (master password salt/verifier)."""

    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
