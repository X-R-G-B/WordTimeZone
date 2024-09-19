FROM python:3.12-slim-bookworm AS base
RUN apt-get update -y \
    && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN mkdir -p /app
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
WORKDIR /app
RUN uv sync --frozen
COPY .data /app/.data
COPY worldtimezone /app/worldtimezone
CMD [ "uv", "run", "python", "-O", "./worldtimezone/__main__.py" ]
