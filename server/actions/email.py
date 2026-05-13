"""Send an email via SMTP."""
from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from typing import Any

from server.actions.base import Action
from server.config import settings


class EmailAction(Action):
    name = "notify_email"

    async def run(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        host = config.get("smtp_host") or settings.smtp_host
        port = int(config.get("smtp_port") or settings.smtp_port)
        user = config.get("smtp_user") or settings.smtp_user
        password = config.get("smtp_pass") or settings.smtp_pass
        sender = config.get("from") or settings.smtp_from or user
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
