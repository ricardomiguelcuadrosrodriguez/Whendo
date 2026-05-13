"""Recipes API.

Endpoints:
    GET    /api/recipes              → list loaded recipes + next-run times
    GET    /api/recipes/errors       → list recipes that failed to load
    POST   /api/recipes              → create a new recipe (saves YAML to disk)
    POST   /api/recipes/reload       → re-scan recipes/ and reschedule
    POST   /api/recipes/{name}/run   → run a recipe right now (manual fire)
    DELETE /api/recipes/{name}       → delete a recipe file from disk
"""
from __future__ import annotations

import asyncio
import re
from pathlib import Path

import yaml
from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import ValidationError

from server.config import settings
from server.db.schema import Recipe
from server.scheduler.executor import run_recipe

router = APIRouter()


def _engine(request: Request):
    """Pull the SchedulerEngine off app.state. Avoids circular imports."""
    return request.app.state.scheduler


def _slugify(name: str) -> str:
    """Convert a recipe name into a safe filename."""
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", name.strip().lower()).strip("-")
    return slug or "recipe"


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
    result = await engine.load_recipes_from_disk(settings.recipes_dir)
    return {
        "loaded": len(result.recipes),
        "errors": len(result.errors),
        "error_files": [str(p) for p, _ in result.errors],
    }


@router.post("")
async def create_recipe(
    request: Request,
    payload: dict = Body(..., description="{'yaml': '<yaml-text>'}"),
) -> dict:
    """Create a new recipe from raw YAML text. Saves it to disk and reloads."""
    yaml_text = payload.get("yaml", "")
    if not yaml_text or not isinstance(yaml_text, str):
        raise HTTPException(
            status_code=400, detail="Missing 'yaml' field in body"
        )

    # 1. Parse YAML
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400, detail="Top-level YAML must be a mapping"
        )

    # 2. Validate schema
    try:
        recipe = Recipe.model_validate(data)
    except ValidationError as e:
        first = e.errors()[0]
        raise HTTPException(
            status_code=400,
            detail=f"Schema error at {first['loc']}: {first['msg']}",
        )

    # 3. Check for duplicate names
    recipes_dir = Path(settings.recipes_dir)
    recipes_dir.mkdir(parents=True, exist_ok=True)
    slug = _slugify(recipe.name)
    target = recipes_dir / f"{slug}.yaml"

    if target.exists():
        raise HTTPException(
            status_code=409,
            detail=f"A recipe with this name already exists: {target.name}",
        )

    # 4. Save the YAML to disk
    target.write_text(yaml_text, encoding="utf-8")

    # 5. Reload the scheduler to pick it up
    engine = _engine(request)
    await engine.load_recipes_from_disk(recipes_dir)

    return {
        "status": "created",
        "name": recipe.name,
        "file": target.name,
    }


@router.delete("/{name}")
async def delete_recipe(name: str, request: Request) -> dict:
    """Delete a recipe by name (removes its file from disk and reloads)."""
    engine = _engine(request)
    recipe = next((r for r in engine.list_recipes() if r.name == name), None)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe '{name}' not found")

    # Find the file (try slugified name first, then any file containing the name)
    recipes_dir = Path(settings.recipes_dir)
    slug = _slugify(name)
    candidates = [recipes_dir / f"{slug}.yaml", recipes_dir / f"{slug}.yml"]
    target = next((c for c in candidates if c.exists()), None)

    if not target:
        # Fallback: scan all files and find the one with matching name
        for yaml_file in list(recipes_dir.glob("*.yaml")) + list(recipes_dir.glob("*.yml")):
            try:
                data = yaml.safe_load(yaml_file.read_text())
                if isinstance(data, dict) and data.get("name") == name:
                    target = yaml_file
                    break
            except Exception:
                continue

    if not target:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find file on disk for '{name}'",
        )

    target.unlink()
    await engine.load_recipes_from_disk(recipes_dir)

    return {"status": "deleted", "name": name, "file": target.name}


@router.post("/{name}/run")
async def run_now(name: str, request: Request) -> dict:
    """Trigger a recipe immediately (out-of-band)."""
    engine = _engine(request)
    recipe = next((r for r in engine.list_recipes() if r.name == name), None)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe '{name}' not found")
    asyncio.create_task(run_recipe(recipe))
    return {"status": "queued", "recipe": name}
