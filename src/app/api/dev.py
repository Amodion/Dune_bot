from __future__ import annotations

from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import FileResponse, HTMLResponse, Response

from app.utils.paths import static_path

router = APIRouter(tags=["dev"])


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Dune Bot API docs",
        swagger_favicon_url="/favicon.ico",
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    path = static_path("favicon.ico")
    if path.exists():
        return FileResponse(path)
    return Response(status_code=204)

