# Use Python 3.10 as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.0

# Configure Poetry: Don't create virtual environment, install to system Python
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set working directory
WORKDIR /app

# Copy Poetry configuration files
COPY ../pyproject.toml ../poetry.lock ./

# Install dependencies
RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

# Copy application code and build files
COPY ../simple_api ./simple_api
COPY ../Makefile ./

# Run the application using make and using a single worker to ensure the proper usage of the mocked DB
CMD ["sh", "-c", "make run ARGS='--n-workers 1'"] 