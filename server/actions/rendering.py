"""Jinja2 rendering for action config values.

Each string field in an action's YAML config is treated as a Jinja2 template
and rendered against the context produced by the source. Non-string values
(numbers, bools, lists, nested dicts) are walked recursively and only string
leaves are rendered. Templates that don't use any variables pass through
unchanged.
"""
from __future__ import annotations

from typing import Any

from jinja2 import Environment, StrictUndefined

_env = Environment(
    autoescape=False,
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        if "{{" not in value and "{%" not in value:
            return value
        return _env.from_string(value).render(**context)
    if isinstance(value, dict):
        return {k: render_value(v, context) for k, v in value.items()}
    if isinstance(value, list):
        return [render_value(v, context) for v in value]
    return value
