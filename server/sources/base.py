"""Base class for sources."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Source(ABC):
    """A source decides whether a recipe should fire and produces context
    variables that the action can use in its Jinja2-rendered config."""

    name: str

    @abstractmethod
    async def check(
        self,
        config: dict[str, Any],
        *,
        recipe_name: str,
    ) -> tuple[bool, dict[str, Any]]:
        """Return (should_fire, context).

        Args:
            config: The source block from the recipe YAML.
            recipe_name: Used by stateful sources to read/write SourceState.

        Returns:
            (True, ctx) → the recipe fires, ctx is passed to the action.
            (False, _)  → the action is skipped.
        """
        ...
