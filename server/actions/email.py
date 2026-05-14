"""Send an email via SMTP."""
from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from typing import Any

from server import settings_service
from server.actions.base import Action
from server.config import settings


class EmailAction(Action):
    name = "notify_email"

    async def run(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        host = settings_service.resolve("smtp.host", recipe_override=config.get("smtp_host"), env_fallback=settings.smtp_host or None)
        port_value = settings_service.resolve("smtp.port", recipe_override=str(config["smtp_port"]) if config.get("smtp_port") else None, env_fallback=str(settings.smtp_port))
        port = int(port_value or 587)
        user = settings_service.resolve("smtp.user", recipe_override=config.get("smtp_user"), env_fallback=settings.smtp_user or None)
        password = settings_service.resolve("smtp.pass", recipe_override=config.get("smtp_pass"), env_fallback=settings.smtp_pass or None)
        sender = settings_service.resolve("smtp.from", recipe_override=config.get("from"), env_fallback=settings.smtp_from or None) or user
        recipient = config.get("to")
        subject = config.get("subject", "")
        body = config.get("body", "")

        if not host:
            raise RuntimeError("smtp_host is not set. Configure SMTP_HOST in .env.")
        if not recipient:
            raise RuntimeError("notify_email requires a 'to' field")
        if not sender:
            raise RuntimeError("notify_email requires a sender (SMTP_FROM or smtp_user)")

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        def _send() -> None:
            with smtplib.SMTP(host, port) as smtp:
                smtp.starttls()
                if user and password:
                    smtp.login(user, password)
                smtp.send_message(msg)

        await asyncio.to_thread(_send)

        return {
            "channel": "email",
            "to": recipient,
            "from": sender,
            "subject": subject,
        }
