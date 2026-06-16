from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheckItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    status: HealthStatus
    message: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: str
    version: str
    status: HealthStatus
    message: str
    checks: list[HealthCheckItem]

