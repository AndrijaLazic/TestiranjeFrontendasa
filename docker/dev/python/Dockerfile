FROM python:3.13-bookworm

ARG APP_UID=1000
ARG APP_GID=1000

# Set working directory
WORKDIR /python-app

# Source code is bind-mounted by docker-compose in development.

ENV UV_PROJECT_ENVIRONMENT=/usr/local

# Install build tools and Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    bubblewrap \
    uidmap \
    && pip install --upgrade pip \
    # dev libraries
    && pip install uv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${APP_GID} app \
    && useradd --uid ${APP_UID} --gid ${APP_GID} --create-home --shell /bin/bash app \
    && chown -R app:app /home/app

ENV HOME=/home/app

USER app
