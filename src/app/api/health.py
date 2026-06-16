from __future__ import annotations

from fastapi import APIRouter, Response, status

from app.schemas.health import HealthResponse, HealthStatus
from app.utils.env_config import get_settings
from app.utils.health_check import build_health_response

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(response: Response) -> HealthResponse:
    settings = get_settings()
    health_response = build_health_response(settings)
    if health_response.status == HealthStatus.UNHEALTHY:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return health_response

