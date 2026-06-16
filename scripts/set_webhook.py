from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from telegram import Bot  # noqa: E402

from app.utils.env_config import get_settings  # noqa: E402


async def main() -> None:
    settings = get_settings()
    token = settings.telegram_bot_token_value
    webhook_url = settings.webhook_url
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required.")
    if not webhook_url:
        raise SystemExit("PUBLIC_BASE_URL is required.")

    bot = Bot(token)
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.telegram_webhook_secret_token_value,
        allowed_updates=["message", "inline_query", "callback_query"],
        drop_pending_updates=False,
    )
    print(f"Webhook set to {webhook_url}")


if __name__ == "__main__":
    asyncio.run(main())

