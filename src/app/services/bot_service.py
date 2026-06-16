from __future__ import annotations

import logging
from typing import Any

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler, InlineQueryHandler

from app.services.bot_handlers import inline_query, roll_command, roll_keyboard_callback, start_or_help
from app.utils.env_config import Settings

logger = logging.getLogger(__name__)


class TelegramBotService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._application: Application[Any, Any, Any, Any, Any, Any] | None = None
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return

        token = self._settings.telegram_bot_token_value
        if not token:
            logger.warning("TELEGRAM_BOT_TOKEN is not configured; webhook processing is disabled.")
            self._initialized = True
            return

        application = ApplicationBuilder().token(token).updater(None).build()
        application.add_handler(CommandHandler(["start", "help"], start_or_help))
        application.add_handler(CommandHandler("roll", roll_command))
        application.add_handler(InlineQueryHandler(inline_query))
        application.add_handler(CallbackQueryHandler(roll_keyboard_callback, pattern=r"^(t-|t\+|n-|n\+|c-|c\+|dt|d-|d\+|r-|r\+|det|roll|noop)\|"))

        await application.initialize()
        await application.start()
        self._application = application
        self._initialized = True

    async def process_update(self, payload: dict[str, Any]) -> None:
        await self.initialize()
        if self._application is None:
            raise RuntimeError("Telegram bot token is not configured.")
        update = Update.de_json(payload, self._application.bot)
        await self._application.process_update(update)

    async def shutdown(self) -> None:
        if self._application is None:
            return
        await self._application.stop()
        await self._application.shutdown()
        self._application = None
        self._initialized = False

