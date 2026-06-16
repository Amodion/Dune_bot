# Dune Bot Engineering Context

This service owns the Telegram webhook for `@duneTTRPG_bot` and Dune: Adventures in the Imperium 2d20 dice roll formatting.

The game logic lives in `src/app/services/dice_service.py` and intentionally preserves the legacy loose parser and output strings from the old Flask/telebot app. The Telegram layer supports `/start`, `/help`, text `/roll ...`, inline `@duneTTRPG_bot ...`, inline `help`, and a stateless inline-button `/roll` wizard.

The runtime app is FastAPI. Vercel imports root `app.py`, which adds `src` to `sys.path` and exposes the ASGI `app` from `app.main`.

Secrets come only from runtime environment variables. The app does not load `.env` files. Webhook registration is manual through `scripts/set_webhook.py` so imports and deployments do not mutate Telegram state.

Telegram supports one active webhook per bot token. Switching between local tunnel testing and Vercel production requires running `scripts/set_webhook.py` with the desired `PUBLIC_BASE_URL`.

