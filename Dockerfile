FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:0.8.11-debian-slim
LABEL authors="forestcat"

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies from pyproject.toml/uv.lock
RUN uv sync

# Create data volume
VOLUME ["/data"]
ENV SIS_DATABASE_FILENAME="/data/sis_database.sqlite"

# Expose default port
EXPOSE 8000

ENTRYPOINT ["uv", "run", "app/main.py"]