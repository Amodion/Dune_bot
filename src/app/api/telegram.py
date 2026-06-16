from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.services.bot_service import TelegramBotService
from app.utils.env_config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook/{path_secret}")
async def telegram_webhook(
    path_secret: str,
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
) -> dict[str, bool]:
    settings = get_settings()
    if path_secret != settings.TELEGRAM_WEBHOOK_PATH_SECRET:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found.")

    expected_secret = settings.telegram_webhook_secret_token_value
    if expected_secret and x_telegram_bot_api_secret_token != expected_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Telegram secret token.")

    payload: dict[str, Any] = await request.json()
    telegram_service: TelegramBotService | None = getattr(request.app.state, "telegram_service", None)
    if telegram_service is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Telegram service is not ready.")

    await telegram_service.process_update(payload)
    return {"ok": True}

