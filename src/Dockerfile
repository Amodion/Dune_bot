# syntax=docker/dockerfile:1

ARG BASE_IMAGE=python:3.12-slim

FROM ${BASE_IMAGE} AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY src/app/requirements.txt ./requirements.txt

RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir -r ./requirements.txt

FROM base AS tests

COPY src/app ./app
COPY tests ./tests

RUN python -m pip install --no-cache-dir -r ./tests/dev_requirements.txt \
    && mkdir -p /app/reports

CMD ["python", "-m", "pytest", "tests", "--junitxml=/app/reports/test_results.xml"]

FROM base AS runtime

COPY src/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
