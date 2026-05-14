"""Send a push notification via ntfy.sh."""
from __future__ import annotations

from typing import Any

import httpx

from server import settings_service
from server.actions.base import Action
from server.config import settings


class NtfyAction(Action):
    name = "notify_ntfy"

    async def run(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        server = settings_service.resolve(
            "ntfy.server",
            recipe_override=config.get("server"),
            env_fallback=settings.ntfy_server or None,
        ) or "https://ntfy.sh"
        topic = settings_service.resolve(
            "ntfy.default_topic",
            recipe_override=config.get("topic"),
            env_fallback=settings.ntfy_default_topic or None,
        )
        message = config.get("message", "")
        title = config.get("title")
        priority = config.get("priority")
        tags = config.get("tags")
        click_url = config.get("click")

        if not topic:
            raise RuntimeError(
                "ntfy topic is not set. Configure NTFY_DEFAULT_TOPIC in .env "
                "or pass topic in the recipe."
            )
        if not message:
            raise RuntimeError("notify_ntfy requires a non-empty 'message' field")

        headers: dict[str, str] = {}
        if title:
            headers["Title"] = title
        if priority:
            headers["Priority"] = str(priority)
        if tags:
            headers["Tags"] = ",".join(tags) if isinstance(tags, list) else str(tags)
        if click_url:
            headers["Click"] = click_url

        url = f"{server.rstrip('/')}/{topic}"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, content=message.encode("utf-8"), headers=headers)
            resp.raise_for_status()

        return {
            "channel": "ntfy",
            "server": server,
            "topic": topic,
            "chars": len(message),
        }
