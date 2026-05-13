"""SchedulerEngine — the heart of whendo's runtime.

Responsibilities:
- Load recipes from disk on startup
- Convert each recipe's `when:` block into an APScheduler trigger
- Schedule the executor to run when the trigger fires
- Provide `reload()` to pick up new/changed/deleted recipes without restart
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from server.db.schema import Recipe
from server.scheduler.executor import run_recipe
from server.scheduler.loader import LoadResult, load_recipes
from server.scheduler.trigger_parser import parse_trigger

logger = logging.getLogger(__name__)


class SchedulerEngine:
    """Wraps APScheduler with whendo-specific logic."""

    def __init__(self) -> None:
        self._scheduler = AsyncIOScheduler()
        self._recipes: dict[str, Recipe] = {}
        self._load_errors: list[tuple[Path, str]] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the underlying scheduler. Must be called from an event loop."""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started")

    async def shutdown(self) -> None:
        """Stop the scheduler. Lets in-flight jobs finish."""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")

    # ------------------------------------------------------------------
    # Recipe management
    # ------------------------------------------------------------------

    async def load_recipes_from_disk(self, recipes_dir: Path | str) -> LoadResult:
        """Load recipes from `recipes_dir` and schedule the enabled ones.

        Clears any previously scheduled jobs first, so this doubles as a
        reload.
        """
        recipes_dir = Path(recipes_dir)
        logger.info(f"Loading recipes from {recipes_dir}")

        # Clear current schedule
        for job in self._scheduler.get_jobs():
            self._scheduler.remove_job(job.id)
        self._recipes.clear()

        result = load_recipes(recipes_dir)
        self._load_errors = result.errors

        for recipe in result.recipes:
            self._schedule(recipe)

        return result

    def _schedule(self, recipe: Recipe) -> None:
        """Schedule one recipe. Skips disabled recipes and on_startup-only ones."""
        if not recipe.enabled:
            logger.info(f"Skipped (disabled): {recipe.name}")
            return

        when = recipe.when

        # on_startup recipes run once now (if also no `every`, they don't get scheduled)
        if when.on_startup:
            asyncio.create_task(run_recipe(recipe))
            logger.info(f"Fired on_startup: {recipe.name}")

        # Webhook-triggered recipes aren't scheduled — they wait for HTTP
        if when.webhook:
            logger.info(f"Webhook-only recipe registered: {recipe.name} (path: {when.webhook})")
            self._recipes[recipe.name] = recipe
            return

        if not when.every:
            # No recurring schedule (only on_startup, already fired)
            self._recipes[recipe.name] = recipe
            return

        try:
            trigger = parse_trigger(when.every)
        except ValueError as e:
            logger.error(f"Cannot schedule '{recipe.name}': {e}")
            self._load_errors.append((Path(f"<{recipe.name}>"), str(e)))
            return

        job_id = f"recipe::{recipe.name}"
        self._scheduler.add_job(
            run_recipe,
            trigger=trigger,
            args=[recipe],
            id=job_id,
            name=recipe.name,
            replace_existing=True,
            max_instances=1,           # don't overlap same recipe with itself
            coalesce=True,             # if we miss many, just run once
            misfire_grace_time=300,    # 5 minutes' grace if server was down
        )

        self._recipes[recipe.name] = recipe
        logger.info(f"Scheduled '{recipe.name}': {when.every}")

    async def fire_webhook(self, webhook_path: str) -> Recipe | None:
        """Manually trigger any recipes registered for `webhook_path`."""
        fired: Recipe | None = None
        for recipe in self._recipes.values():
            if recipe.when.webhook == webhook_path and recipe.enabled:
                asyncio.create_task(run_recipe(recipe))
                fired = recipe
        return fired

    # ------------------------------------------------------------------
    # Introspection (for the API)
    # ------------------------------------------------------------------

    def list_recipes(self) -> list[Recipe]:
        return list(self._recipes.values())

    def list_load_errors(self) -> list[tuple[Path, str]]:
        return list(self._load_errors)

    def next_run_for(self, recipe_name: str):
        """Return the next scheduled run time for a recipe, or None."""
        job = self._scheduler.get_job(f"recipe::{recipe_name}")
        return job.next_run_time if job else None
