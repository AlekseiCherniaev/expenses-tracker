from fastapi import APIRouter
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.responses import HTMLResponse

router = APIRouter(tags=["docs"])


@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/internal/openapi.json",
        title="Expenses Tracker API",
        swagger_css_url="static/swagger-ui.css",
        swagger_js_url="static/swagger-ui-bundle.js",
        swagger_favicon_url="static/fastapi.png",
    )
