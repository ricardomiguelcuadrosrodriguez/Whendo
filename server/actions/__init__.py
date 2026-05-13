"""Action registry. Each action runs after a recipe's source fires."""
from __future__ import annotations

from server.actions.base import Action
from server.actions.email import EmailAction
from server.actions.ntfy import NtfyAction
from server.actions.telegram import TelegramAction

ACTIONS: dict[str, Action] = {
    "notify_telegram": TelegramAction(),
    "notify_ntfy": NtfyAction(),
    "notify_email": EmailAction(),
}

__all__ = ["ACTIONS", "Action"]
