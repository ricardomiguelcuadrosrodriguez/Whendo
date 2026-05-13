"""Executes a recipe: source → condition → action.

For v0.1.0 this is a STUB. It validates the flow and records runs in the DB,
but the actual source/action calls are placeholders that just log.

Real sources/actions are wired in once we add the source/action registry.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from server.db.connection import get_session
from server.db.schema import Recipe, Run

logger = logging.getLogger(__name__)


async def run_recipe(recipe: Recipe) -> None:
    """Execute one cycle of a recipe and persist the run.

    Flow:
        1. Resolve source (if any) and check its condition.
        2. If condition matches (or no source), run the action.
        3. Persist a Run row regardless of outcome.
    """
    started = datetime.now(timezone.utc)
    status = "running"
    error: str | None = None
    output: dict | None = None

    logger.info(f"[run] Starting recipe: {recipe.name}")

    try:
        context: dict = {}

        # --- Step 1: Source (optional) ---
        source_name = recipe.source_name
        if source_name:
            logger.info(f"[run] {recipe.name}: would check source '{source_name}' (stub)")
            # TODO(sources): call sources[source_name].check(recipe.if_.<source>)
            # For now, assume the condition matched.
            context["_stub"] = True

        # --- Step 2: Action ---
        action_name = recipe.action_name
        logger.info(f"[run] {recipe.name}: would run action '{action_name}' (stub)")
        # TODO(actions): call actions[action_name].run(recipe.then.<action>, context)

        status = "success"
        output = {
            "source": source_name,
            "action": action_name,
            "stub": True,
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
