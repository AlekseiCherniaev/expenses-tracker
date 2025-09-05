FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["/app/.venv/bin/uvicorn", "expenses_tracker.app:init_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-use-colors"]