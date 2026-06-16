# ДюнаБот

FastAPI Telegram webhook service for **Дюна: Приключения в Империи** dice rolls.

The old Flask/telebot PythonAnywhere app has been replaced with an async FastAPI app using `python-telegram-bot`. Game logic and legacy text syntax are preserved, and `/roll` now also opens a button-based roll wizard.

## Bot Usage

- `/start` or `/help` sends help.
- `/roll` opens the interactive keyboard.
- `/roll 15 n4 c6 d3 r18 !` rolls from text.
- Inline mode still works: `@duneTTRPG_bot 15 n4 c6 d3 r18 !`.
- Inline help still works: `@duneTTRPG_bot help`.

Legacy syntax:

```text
@duneTTRPG_bot T nX cY dZ rV !
```

- `T` - порог успеха
- `X` - число кубиков, default `2`
- `Y` - критический успех, default `1`
- `Z` - сложность проверки
- `V` - затруднения, default `20`
- `!` - потрачена Решимость

## Environment

The app reads configuration from runtime environment variables only. It does not load `.env` files automatically.

| Variable | Required | Description |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | yes for bot runtime | Bot token from BotFather. |
| `TELEGRAM_WEBHOOK_PATH_SECRET` | yes | Secret path segment for `/telegram/webhook/{secret}`. |
| `TELEGRAM_WEBHOOK_SECRET_TOKEN` | recommended | Telegram `secret_token`, checked from `X-Telegram-Bot-Api-Secret-Token`. |
| `PUBLIC_BASE_URL` | for webhook scripts | Public Vercel or tunnel URL without trailing slash. |
| `SERVICE_VERSION` | no | Runtime version, default `0.1.0`. |
| `LOG_LEVEL` | no | Default `INFO`. |

See `.env.example` for a full template.

## Local Development

Install dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest
```

Run the API:

```powershell
uvicorn app:app --reload
```

Health check:

```powershell
curl.exe --noproxy * http://127.0.0.1:8000/health
```

## Webhook Testing

Telegram supports one active webhook per bot token. Switching between local and production means setting the webhook again.

For local testing:

1. Start the app with `uvicorn app:app --reload`.
2. Expose it with a tunnel such as ngrok or cloudflared.
3. Set:

```powershell
$env:PUBLIC_BASE_URL="https://your-tunnel.example"
$env:TELEGRAM_BOT_TOKEN="..."
$env:TELEGRAM_WEBHOOK_PATH_SECRET="..."
$env:TELEGRAM_WEBHOOK_SECRET_TOKEN="..."
python scripts/set_webhook.py
```

Inspect current Telegram webhook:

```powershell
python scripts/get_webhook_info.py
```

## Vercel Deployment

The repository is ready for Vercel Git deployments:

- root `app.py` exposes the ASGI app
- `pyproject.toml` declares Python `>=3.12` and runtime dependencies
- `vercel.json` excludes tests and caches from the function bundle

In Vercel Project Settings, configure the Telegram environment variables. Production branch deploys become production deployments; other branches become preview deployments. After deploying the desired URL, set the Telegram webhook with `scripts/set_webhook.py`.

## Docker Import Check

```powershell
docker compose up --build import-check
```

## Notes

- `src/app/services/dice_service.py` intentionally keeps the legacy loose parser and output spelling, including `treshold`.
- Webhook registration is never done at import time.
- PythonAnywhere proxy and absolute file paths were removed.
