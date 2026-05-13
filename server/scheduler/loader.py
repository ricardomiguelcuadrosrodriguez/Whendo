"""Loads recipes from disk.

Reads every *.yaml / *.yml file in `recipes_dir`, parses it, and validates
it against the Recipe schema. Invalid recipes are logged but do NOT block
the load — other recipes keep working.
"""
from __future__ import annotations

import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from server.db.schema import Recipe

logger = logging.getLogger(__name__)


class LoadResult:
    """The result of loading recipes from a directory."""

    def __init__(self) -> None:
        self.recipes: list[Recipe] = []
        self.errors: list[tuple[Path, str]] = []

    @property
    def summary(self) -> str:
        return f"{len(self.recipes)} loaded, {len(self.errors)} failed"


def load_recipes(recipes_dir: Path) -> LoadResult:
    """Load and validate all recipes from `recipes_dir`.

    Returns a LoadResult with both the successfully-loaded recipes and a
    list of (file_path, error_message) tuples for the ones that failed.
    """
    result = LoadResult()
    recipes_dir = Path(recipes_dir)

    if not recipes_dir.exists():
        logger.warning(f"recipes_dir does not exist: {recipes_dir}")
        return result

    yaml_files = sorted(
        list(recipes_dir.glob("*.yaml")) + list(recipes_dir.glob("*.yml"))
    )

    if not yaml_files:
        logger.info(f"No recipes found in {recipes_dir}")
        return result

    seen_names: set[str] = set()

    for yaml_file in yaml_files:
        try:
            raw = yaml_file.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)

            if data is None:
                raise ValueError("File is empty")
            if not isinstance(data, dict):
                raise ValueError(f"Top-level YAML must be a mapping, got {type(data).__name__}")

            recipe = Recipe.model_validate(data)

            if recipe.name in seen_names:
                raise ValueError(
                    f"Duplicate recipe name '{recipe.name}' "
                    f"(already loaded from another file)"
                )
            seen_names.add(recipe.name)

            result.recipes.append(recipe)
            logger.info(f"Loaded recipe '{recipe.name}' from {yaml_file.name}")

        except yaml.YAMLError as e:
            msg = f"YAML parse error: {e}"
            result.errors.append((yaml_file, msg))
            logger.error(f"Failed to load {yaml_file.name}: {msg}")

        except ValidationError as e:
            msg = f"Schema validation error: {e.errors()[0]['msg']} at {e.errors()[0]['loc']}"
            result.errors.append((yaml_file, msg))
            logger.error(f"Failed to load {yaml_file.name}: {msg}")

        except Exception as e:
            msg = f"{type(e).__name__}: {e}"
            result.errors.append((yaml_file, msg))
            logger.error(f"Failed to load {yaml_file.name}: {msg}")

    logger.info(f"Recipe load complete: {result.summary}")
    return result
