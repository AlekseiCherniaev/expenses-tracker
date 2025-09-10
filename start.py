from uvicorn import run

from expenses_tracker.app import init_app
from expenses_tracker.core.settings import settings

if __name__ == "__main__":
    run(init_app(), host=settings.app_host, port=settings.app_port)
