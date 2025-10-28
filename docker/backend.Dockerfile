FROM python:3.11-slim

WORKDIR /app

# Install uv (Astral) and minimal tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
  && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"
ENV UV_LINK_MODE=copy

# Leverage Docker layer caching: copy manifests first and sync deps
COPY pyproject.toml uv.lock README.md ./

# Create project venv and install deps from lockfile
RUN uv venv && . .venv/bin/activate && uv sync --frozen

# Now copy source code
COPY app ./app

EXPOSE 8000

# Run via uv using the project environment
CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
