"""Recipes API.

Endpoints:
    GET  /api/recipes              → list loaded recipes + next-run times
    GET  /api/recipes/errors       → list recipes that failed to load
    POST /api/recipes/reload       → re-scan recipes/ and reschedule
    POST /api/recipes/{name}/run   → run a recipe right now (manual fire)
"""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Request

from server.scheduler.executor import run_recipe

router = APIRouter()


def _engine(request: Request):
    """Pull the SchedulerEngine off app.state. Avoids circular imports."""
    return request.app.state.scheduler


@router.get("")
async def list_recipes(request: Request) -> list[dict]:
    engine = _engine(request)
    out: list[dict] = []
    for recipe in engine.list_recipes():
        next_run = engine.next_run_for(recipe.name)
        out.append({
            "name": recipe.name,
            "description": recipe.description,
            "enabled": recipe.enabled,
            "when": recipe.when.model_dump(exclude_none=True),
            "source": recipe.source_name,
            "action": recipe.action_name,
            "next_run": next_run.isoformat() if next_run else None,
        })
    return out


@router.get("/errors")
async def list_errors(request: Request) -> list[dict]:
    engine = _engine(request)
    return [{"file": str(p), "error": msg} for p, msg in engine.list_load_errors()]


@router.post("/reload")
async def reload(request: Request) -> dict:
    engine = _engine(request)
    from server.config import settings
    result = await engine.load_recipes_from_disk(settings.recipes_dir)
    return {
        "loaded": len(result.recipes),
        "errors": len(result.errors),
        "error_files": [str(p) for p, _ in result.errors],
    }


@router.post("/{name}/run")
async def run_now(name: str, request: Request) -> dict:
    """Trigger a recipe immediately (out-of-band)."""
    engine = _engine(request)
    recipe = next((r for r in engine.list_recipes() if r.name == name), None)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe '{name}' not found")
    asyncio.create_task(run_recipe(recipe))
    return {"status": "queued", "recipe": name}
