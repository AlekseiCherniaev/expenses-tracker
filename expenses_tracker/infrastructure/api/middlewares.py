from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(SlowAPIMiddleware)
