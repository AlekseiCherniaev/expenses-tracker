from uvicorn import run

from expenses_tracker.app import init_app

if __name__ == "__main__":
    run(init_app(), host="127.0.0.1", port=8000)
