"""Tests for the recipe loader."""
from pathlib import Path

import pytest

from server.scheduler.loader import load_recipes


VALID_RECIPE = """
name: "Test recipe"
when:
  every: "5 minutes"
then:
  notify_ntfy:
    topic: "test"
"""

VALID_RECIPE_WITH_IF = """
name: "Test with source"
when:
  every: "day at 7am"
if:
  weather:
    location: "Lima, PE"
    condition: "rain_today"
then:
  notify_telegram:
    message: "test"
"""

INVALID_NO_WHEN = """
name: "Missing when"
then:
  notify_ntfy:
    topic: "test"
"""

INVALID_YAML = """
name: "Broken: : : YAML
when:
"""


def test_empty_dir(tmp_path: Path):
    result = load_recipes(tmp_path)
    assert result.recipes == []
    assert result.errors == []


def test_missing_dir(tmp_path: Path):
    result = load_recipes(tmp_path / "does-not-exist")
    assert result.recipes == []
    assert result.errors == []


def test_loads_valid_recipe(tmp_path: Path):
    (tmp_path / "recipe.yaml").write_text(VALID_RECIPE)
    result = load_recipes(tmp_path)
    assert len(result.recipes) == 1
    assert result.recipes[0].name == "Test recipe"
    assert result.errors == []


def test_loads_valid_recipe_with_if(tmp_path: Path):
    (tmp_path / "recipe.yaml").write_text(VALID_RECIPE_WITH_IF)
    result = load_recipes(tmp_path)
    assert len(result.recipes) == 1
    assert result.recipes[0].source_name == "weather"
    assert result.recipes[0].action_name == "notify_telegram"


def test_invalid_schema_is_logged_not_raised(tmp_path: Path):
    (tmp_path / "bad.yaml").write_text(INVALID_NO_WHEN)
    result = load_recipes(tmp_path)
    assert result.recipes == []
    assert len(result.errors) == 1


def test_invalid_yaml_is_logged_not_raised(tmp_path: Path):
    (tmp_path / "broken.yaml").write_text(INVALID_YAML)
    result = load_recipes(tmp_path)
    assert result.recipes == []
    assert len(result.errors) == 1


def test_one_bad_recipe_does_not_block_others(tmp_path: Path):
    (tmp_path / "good.yaml").write_text(VALID_RECIPE)
    (tmp_path / "bad.yaml").write_text(INVALID_NO_WHEN)
    result = load_recipes(tmp_path)
    assert len(result.recipes) == 1
    assert len(result.errors) == 1


def test_duplicate_names_rejected(tmp_path: Path):
    (tmp_path / "a.yaml").write_text(VALID_RECIPE)
    (tmp_path / "b.yaml").write_text(VALID_RECIPE)  # same name
    result = load_recipes(tmp_path)
    assert len(result.recipes) == 1
    assert len(result.errors) == 1
    assert "Duplicate" in result.errors[0][1]
