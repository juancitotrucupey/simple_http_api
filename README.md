# Traffic Tracker

Basic example of a traffic tracker for a website.

## Installation

This project uses Poetry for dependency management. Follow these steps to set up the development environment:

### Prerequisites

- Python 3.10-3.12
- Poetry (install from https://python-poetry.org/docs/#installation)

### Setup

1. Install dependencies:
   ```bash
   poetry lock
   poetry install --no-root
   ```

2. Install development dependencies (includes ruff for formatting):
   ```bash
   poetry install --no-root --with dev
   ```

## Development

### Code Formatting

This project uses Ruff for code formatting and linting.

#### Format code using ruff directly:
```bash
poetry run ruff format .
poetry run ruff check --fix .
```

#### Format code using the Makefile:
```bash
make format
```

### Project Structure

- `simple_api/` - Main source code directory
- `docker/` - Docker configuration files
- `pyproject.toml` - Project configuration and dependencies
- `Makefile` - Development automation commands

## Running the Application

(Instructions for running the application will be added as the project develops) 