"""Recipe schema. The heart of whendo.

A Recipe is a YAML file with three blocks:
    when:  the trigger (a schedule, a webhook, a poll interval)
    if:    optional source + condition (check weather, RSS, etc.)
    then:  the action (send a notification, hit a webhook, etc.)
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class WhenBlock(BaseModel):
    """When should we check? (the trigger)"""
    every: str | None = None      # "day at 7am" | "5 minutes" | cron expression
    webhook: str | None = None    # path for a webhook trigger
    on_startup: bool = False      # run once at server start

    model_config = {"extra": "forbid"}


class IfBlock(BaseModel):
    """Optional condition source. Exactly one source key must be set."""
    weather: dict[str, Any] | None = None
    rss: dict[str, Any] | None = None
    github_releases: dict[str, Any] | None = None
    spotify_new_release: dict[str, Any] | None = None
    web_scrape: dict[str, Any] | None = None
    http_get: dict[str, Any] | None = None

    model_config = {"extra": "allow"}  # allow future sources without schema bumps


class ThenBlock(BaseModel):
    """The action to run. Exactly one action key must be set."""
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
    """A complete recipe loaded from YAML."""
    name: str = Field(..., description="Human-readable name")
    description: str | None = None
    enabled: bool = True
    when: WhenBlock
    if_: IfBlock | None = Field(default=None, alias="if")
    then: ThenBlock

    model_config = {"populate_by_name": True}


class RecipeRun(BaseModel):
    """One execution of a recipe."""
    recipe_name: str
    started_at: str
    finished_at: str | None = None
    status: str  # "success" | "failed" | "skipped" | "running"
    error: str | None = None
    output: dict[str, Any] | None = None
