from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api import dev, health, telegram
from app.services.bot_service import TelegramBotService
from app.utils.env_config import get_settings
from app.utils.logs import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings)

    telegram_service = TelegramBotService(settings)
    await telegram_service.initialize()
    app.state.telegram_service = telegram_service

    try:
        yield
    finally:
        await telegram_service.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    application = FastAPI(
        title=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        description="Telegram bot webhook service for Dune: Adventures in the Imperium dice rolls.",
        docs_url=None,
        redoc_url=None,
        lifespan=lifespan,
    )
    application.include_router(dev.router)
    application.include_router(health.router)
    application.include_router(telegram.router)
    return application


app = create_app()

