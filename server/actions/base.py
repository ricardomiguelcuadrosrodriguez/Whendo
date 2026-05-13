"""Base class for actions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Action(ABC):
    """An action runs after a recipe's source fires (or unconditionally)."""

    name: str

    @abstractmethod
    async def run(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Execute the action.

        Args:
            config: The action block from the recipe YAML (already Jinja-rendered).
            context: Variables produced by the source, used for templating.

        Returns:
            A small result dict that ends up in Run.output.
        """
        ...
