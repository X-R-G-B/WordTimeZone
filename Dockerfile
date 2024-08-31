FROM python:3.12-slim-bookworm as base

FROM base as builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
COPY . /app
WORKDIR /app
RUN uv sync --frozen
CMD [ "uv", "run", "./worldtimezone/__main__.py" ]
