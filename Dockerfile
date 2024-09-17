FROM python:3.12-slim-bookworm AS base

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY pyproject.toml uv.lock /app
WORKDIR /app
RUN uv sync --frozen
COPY . /app
CMD [ "uv", "run", "./worldtimezone/__main__.py" ]
