from __future__ import annotations

from app.schemas.health import HealthCheckItem, HealthResponse, HealthStatus
from app.utils.env_config import Settings


def build_health_response(settings: Settings) -> HealthResponse:
    checks = [
        HealthCheckItem(name="settings", status=HealthStatus.HEALTHY, message="Settings loaded."),
    ]

    if settings.telegram_bot_token_value:
        checks.append(HealthCheckItem(name="telegram_token", status=HealthStatus.HEALTHY, message="Bot token is configured."))
    else:
        checks.append(HealthCheckItem(name="telegram_token", status=HealthStatus.DEGRADED, message="Bot token is not configured."))

    overall = HealthStatus.HEALTHY
    if any(check.status == HealthStatus.UNHEALTHY for check in checks):
        overall = HealthStatus.UNHEALTHY
    elif any(check.status == HealthStatus.DEGRADED for check in checks):
        overall = HealthStatus.DEGRADED

    return HealthResponse(
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION,
        status=overall,
        message=settings.HEALTH_MESSAGE,
        checks=checks,
    )

