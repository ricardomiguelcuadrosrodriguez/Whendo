"""Executes a recipe: source → condition → action.

Flow:
    1. If the recipe has a source, run it. If it returns False, mark the run
       as 'skipped' and stop.
    2. Render every string in the action config as a Jinja2 template using
       the context produced by the source (empty dict when there's no source).
    3. Dispatch to the registered action.
    4. Persist a Run row capturing status, output and any error.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from server.actions import ACTIONS
from server.actions.rendering import render_value
from server.db.connection import get_session
from server.db.schema import Recipe, Run
from server.sources import SOURCES

logger = logging.getLogger(__name__)


async def run_recipe(recipe: Recipe) -> None:
    started = datetime.now(timezone.utc)
    status = "running"
    error: str | None = None
    output: dict | None = None

    logger.info(f"[run] Starting recipe: {recipe.name}")

    try:
        context: dict = {}

        source_name = recipe.source_name
        if source_name:
            source = SOURCES.get(source_name)
            if source is None:
                raise RuntimeError(f"Unknown source '{source_name}'")
            source_config = recipe.if_.model_dump(exclude_none=True)[source_name]
            should_fire, context = await source.check(
                source_config, recipe_name=recipe.name
            )
            if not should_fire:
                status = "skipped"
                output = {"source": source_name, "reason": "condition_not_met", "context": context}
                logger.info(f"[run] {recipe.name}: skipped (source returned False)")
                return

        action_name = recipe.action_name
        action = ACTIONS.get(action_name)
        if action is None:
            raise RuntimeError(f"Unknown action '{action_name}'")
        raw_action_config = recipe.then.model_dump(exclude_none=True)[action_name]
        rendered_config = render_value(raw_action_config, context)

        result = await action.run(rendered_config, context)

        status = "success"
        output = {
            "source": source_name,
            "action": action_name,
            "context": context,
            "result": result,
        }

    except Exception as e:
        status = "failed"
        error = f"{type(e).__name__}: {e}"
        logger.exception(f"[run] {recipe.name} failed")

    finally:
        finished = datetime.now(timezone.utc)
        with get_session() as session:
            session.add(
                Run(
                    recipe_name=recipe.name,
                    started_at=started,
                    finished_at=finished,
                    status=status,
                    error=error,
                    output=output,
                )
            )
        logger.info(f"[run] {recipe.name}: {status}")
