from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app
from app.utils.env_config import get_settings


def test_health() -> None:
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "dune-bot"


def test_webhook_rejects_wrong_path_secret() -> None:
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.post("/telegram/webhook/wrong", json={"update_id": 1})
    assert response.status_code == 404


def test_webhook_rejects_wrong_secret_header(monkeypatch) -> None:
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET_TOKEN", "expected")
    get_settings.cache_clear()
    client = TestClient(create_app())
    response = client.post(
        "/telegram/webhook/local-dev-webhook",
        json={"update_id": 1},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong"},
    )
    assert response.status_code == 403
    get_settings.cache_clear()


def test_webhook_accepts_valid_update(monkeypatch) -> None:
    processed: list[dict] = []

    async def fake_process_update(self, payload: dict) -> None:
        processed.append(payload)

    monkeypatch.setattr("app.services.bot_service.TelegramBotService.process_update", fake_process_update)
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.post("/telegram/webhook/local-dev-webhook", json={"update_id": 1})
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert processed == [{"update_id": 1}]
