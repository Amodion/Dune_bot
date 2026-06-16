from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener, urlopen

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dotenv import load_dotenv  # noqa: E402


def main() -> None:
    load_dotenv(ROOT / ".env")

    public_base_url = required_env("PUBLIC_BASE_URL").rstrip("/")
    path_secret = required_env("TELEGRAM_WEBHOOK_PATH_SECRET")
    header_secret = required_env("TELEGRAM_WEBHOOK_SECRET_TOKEN")
    bot_token = required_env("TELEGRAM_BOT_TOKEN")

    opener = build_proxy_opener()
    open_url = opener.open if opener else urlopen

    print("Using proxy:", bool(opener))
    print("Base URL:", public_base_url)
    print()

    health = get_json(open_url, f"{public_base_url}/health")
    report("GET /health", health)

    configured_webhook = post_json(
        open_url,
        f"{public_base_url}/telegram/webhook/{path_secret}",
        {"update_id": 123456789},
        header_secret,
    )
    report("POST configured webhook path", configured_webhook)

    fallback_webhook = post_json(
        open_url,
        f"{public_base_url}/telegram/webhook/local-dev-webhook",
        {"update_id": 123456790},
        header_secret,
    )
    report("POST fallback local-dev-webhook path", fallback_webhook)

    webhook_info = get_json(open_url, f"https://api.telegram.org/bot{bot_token}/getWebhookInfo")
    report("Telegram getWebhookInfo", webhook_info)

    print()
    explain(configured_webhook, fallback_webhook)


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} is required. Set it in .env or in your shell.")
    return value


def build_proxy_opener() -> Any | None:
    proxy_config = {}
    if os.environ.get("HTTPS_PROXY"):
        proxy_config["https"] = os.environ["HTTPS_PROXY"]
    if os.environ.get("HTTP_PROXY"):
        proxy_config["http"] = os.environ["HTTP_PROXY"]
    if not proxy_config:
        return None
    return build_opener(ProxyHandler(proxy_config))


def get_json(open_url: Any, url: str) -> dict[str, Any]:
    return request_json(open_url, Request(url, method="GET"))


def post_json(open_url: Any, url: str, payload: dict[str, Any], header_secret: str) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Telegram-Bot-Api-Secret-Token": header_secret,
        },
        method="POST",
    )
    return request_json(open_url, request)


def request_json(open_url: Any, request: Request) -> dict[str, Any]:
    try:
        with open_url(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "ok": True,
                "status": response.status,
                "body": parse_body(body),
            }
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status": exc.code,
            "body": parse_body(body),
        }
    except URLError as exc:
        return {
            "ok": False,
            "status": None,
            "body": str(exc),
        }


def parse_body(body: str) -> Any:
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def report(name: str, result: dict[str, Any]) -> None:
    print(f"== {name} ==")
    print("status:", result["status"])
    print("body:", json.dumps(result["body"], ensure_ascii=False, indent=2))
    print()


def explain(configured_webhook: dict[str, Any], fallback_webhook: dict[str, Any]) -> None:
    configured_status = configured_webhook["status"]
    fallback_status = fallback_webhook["status"]

    if configured_status == 200:
        print("Configured webhook path works. Telegram should stop reporting 404 after the next successful update.")
        return

    if configured_status == 403:
        print("Configured path exists, but TELEGRAM_WEBHOOK_SECRET_TOKEN does not match the request header.")
        return

    if configured_status == 404 and fallback_status != 404:
        print("Vercel is probably using the default TELEGRAM_WEBHOOK_PATH_SECRET=local-dev-webhook.")
        print("Set TELEGRAM_WEBHOOK_PATH_SECRET in Vercel Production and redeploy.")
        return

    if configured_status == 404:
        print("Configured path returns 404. Check Vercel env vars and confirm the latest deployment is serving this code.")
        return

    print("Unexpected result. Check the status/body above and Vercel function logs.")


if __name__ == "__main__":
    main()

