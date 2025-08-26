FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:0.8.11-debian-slim
LABEL authors="forestcat"

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies from pyproject.toml/uv.lock
RUN uv sync

# Expose default port
EXPOSE 8000

# Run the app via gunicorn using uvicorn worker
ENTRYPOINT ["uv", "run"]
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "main:app"]
