"""Send a message via Telegram bot."""
from __future__ import annotations

from typing import Any

from telegram import Bot
from telegram.constants import ParseMode

from server.actions.base import Action
from server.config import settings


class TelegramAction(Action):
    name = "notify_telegram"

    async def run(self, config: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        bot_token = config.get("bot_token") or settings.telegram_bot_token
        chat_id = config.get("chat_id") or settings.telegram_default_chat_id
        message = config.get("message", "")
        parse_mode_str = config.get("parse_mode")

        if not bot_token:
            raise RuntimeError(
                "telegram_bot_token is not set. Configure TELEGRAM_BOT_TOKEN in .env "
                "or pass bot_token in the recipe."
            )
        if not chat_id:
            raise RuntimeError(
                "telegram chat_id is not set. Configure TELEGRAM_DEFAULT_CHAT_ID in .env "
                "or pass chat_id in the recipe."
            )
        if not message:
            raise RuntimeError("notify_telegram requires a non-empty 'message' field")

        parse_mode = None
        if parse_mode_str:
            parse_mode = ParseMode(parse_mode_str.lower())

        bot = Bot(token=bot_token)
        async with bot:
            sent = await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode,
            )

        return {
            "channel": "telegram",
            "chat_id": chat_id,
            "message_id": sent.message_id,
            "chars": len(message),
        }
