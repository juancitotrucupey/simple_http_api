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

## Running the HTTP API

### Starting the Server

1. **Using the run script (Recommended):**
   ```bash
   poetry run python -m simple_api.run
   ```

2. **Using uvicorn directly:**
   ```bash
   poetry run uvicorn simple_api.main:app --host 0.0.0.0 --port 8080 --reload
   ```

The API will be available at: **http://localhost:8080**

### API Documentation

- **Interactive API Documentation (Swagger):** http://localhost:8080/docs
- **Alternative Documentation (ReDoc):** http://localhost:8080/redoc

### API Endpoints

#### 1. **POST /visit** - Log a user visit
Logs a user visit and increments the visit counter.

**Request Body:**
```json
{
  "user_id": "unique_user_id",
  "page_url": "https://example.com/page",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "referrer": "https://google.com"
}
```

**Response:**
```json
{
  "success": true,
  "visit_count": 42,
  "message": "Visit logged successfully. Total visits: 42"
}
```

**Example curl command:**
```bash
curl -X POST http://localhost:8080/visit \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "page_url": "https://example.com/home"}'
```

#### 2. **GET /stats** - Get server statistics
Returns comprehensive server statistics including uptime and visit counts.

**Query Parameters:**
- `timeframe_hours` (optional): Timeframe in hours for recent visits calculation
  - Default: `1.0` (1 hour)
  - Minimum: `0.1` (6 minutes) 
  - Maximum: `168.0` (1 week)

**Response:**
```json
{
  "uptime_seconds": 3600.5,
  "uptime_formatted": "1h 0m 0s",
  "total_visits": 42,
  "current_time": "2023-12-07T10:30:00.123456",
  "server_status": "running",
  "recent_visits": 10,
  "timeframe_hours": 1.0
}
```

**Example curl commands:**
```bash
# Default stats (1 hour timeframe for recent visits)
curl http://localhost:8080/stats

# Custom timeframe (30 minutes for recent visits)
curl "http://localhost:8080/stats?timeframe_hours=0.5"

# Weekly stats (7 days for recent visits)  
curl "http://localhost:8080/stats?timeframe_hours=168.0"
```

#### 3. **GET /health** - Health check
Simple health check endpoint for monitoring.

**Example curl command:**
```bash
curl http://localhost:8080/health
```

### Testing the API

1. **Start the server:**
   ```bash
   poetry run python -m simple_api.run
   ```

2. **Test logging a visit:**
   ```bash
   curl -X POST http://localhost:8080/visit \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_user", "page_url": "https://example.com/test"}'
   ```

3. **Check statistics:**
   ```bash
   # Default stats (1 hour recent visits)
   curl http://localhost:8080/stats
   
   # Custom timeframe stats (30 minutes recent visits)
   curl "http://localhost:8080/stats?timeframe_hours=0.5"
   ```

### Architecture Notes

- **Thread Safety:** Uses multiprocessing.Manager with locks to prevent race conditions
- **MockedDB:** Simulates an external database using shared memory objects
- **FastAPI:** Provides automatic API documentation and request validation
- **Pydantic:** Ensures type safety for request/response models
- **StatsRequest Model:** Uses Pydantic model validation for query parameters via dependency injection
- **Parameter Validation:** Automatically validates timeframe_hours range (0.1-168.0) with detailed error messages 