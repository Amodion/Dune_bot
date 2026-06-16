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
    if not token:
        raise SystemExit("TELEGRAM_BOT_TOKEN is required.")

    bot = Bot(token)
    info = await bot.get_webhook_info()
    print(info.to_json())


if __name__ == "__main__":
    asyncio.run(main())

