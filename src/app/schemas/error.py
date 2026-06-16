from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    message: str
    details: dict[str, Any] | None = None

