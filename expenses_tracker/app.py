from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.staticfiles import StaticFiles

from expenses_tracker.routers.main_router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield

def use_handler_name_as_unique_id(route: APIRoute):
    return f"{route.name}"

def main():
    app = FastAPI(
        title="Expenses Tracker",
        description="API for Expenses Tracker",
        docs_url=None,
        redoc_url=None,
        openapi_url="/internal/openapi.json",
        swagger_ui_oauth2_redirect_url="/internal/docs/oauth2-redirect",
        generate_unique_id_function=use_handler_name_as_unique_id,
        lifespan=lifespan,
    )
    app.mount("/internal/static", StaticFiles(directory="static"), name="static")
    app.include_router(router=router)
    return app

if __name__ == "__main__":
    main()