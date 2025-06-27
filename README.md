# E-commerce Promotion API

API for tracking user visits during e-commerce promotion campaigns. This system tracks customer interactions and displays visitor counts as part of publicity efforts to encourage more participation in promotional events.

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

The Traffic Tracker API can be started in multiple ways, depending on your needs:

#### 1. **Using the run script (Recommended)**

**Default mode (4 workers, no reload):**
```bash
poetry run python -m simple_api.run
# OR using make
make run
```

**Development mode (with auto-reload):**
```bash
poetry run python -m simple_api.run --dev
# OR using make
make run-dev
```

**Custom number of workers:**
```bash
# 8 workers, no reload
poetry run python -m simple_api.run --n-workers 8

# 2 workers with development mode
poetry run python -m simple_api.run --n-workers 2 --dev

# Using make with custom arguments
make run ARGS="--n-workers 8 --dev"
```

#### 2. **Using FastAPI CLI**

**Default FastAPI CLI (4 workers, no reload):**
```bash
poetry run python -m simple_api.run --fastapi-cli
# OR using make
make run-fastapi
```

**FastAPI CLI with development mode:**
```bash
poetry run python -m simple_api.run --fastapi-cli --dev
# OR using make
make run-fastapi-dev
```

**FastAPI CLI with custom workers:**
```bash
# 8 workers, no reload
poetry run python -m simple_api.run --fastapi-cli --n-workers 8

# Custom workers with development mode
poetry run python -m simple_api.run --fastapi-cli --n-workers 2 --dev

# Using make with custom arguments
make run-fastapi ARGS="--n-workers 8"
```

**Direct FastAPI CLI (without run script):**
```bash
# Production mode
poetry run fastapi run --workers 4 --port 8080 simple_api/main.py

# Development mode with reload
poetry run fastapi run --workers 4 --port 8080 --reload simple_api/main.py
```

#### 3. **Using uvicorn directly:**
```bash
poetry run uvicorn simple_api.main:app --host 0.0.0.0 --port 8080 --reload
```

### Command Line Options

The `run.py` script supports the following options:

- `--n-workers N`: Number of worker processes (default: 4)
- `--dev`: Enable development mode with automatic reload on code changes
- `--fastapi-cli`: Use FastAPI CLI instead of uvicorn directly
- `--help`: Show help message with examples

**Important Notes:**
- When `--dev` is used without specifying `--n-workers`, it automatically defaults to 1 worker
- If you explicitly specify `--n-workers` with `--dev`, it must be set to 1 (validation will raise an error otherwise)
- Development mode (`--dev`) makes the server reload automatically when code changes are detected
- Production deployments should avoid using `--dev` flag for better performance

**Validation Rules:**
- `--dev` mode requires exactly 1 worker due to reload mechanism incompatibility with multiple processes
- The system will raise a `ValueError` with detailed instructions if you try to use `--dev` with `--n-workers > 1`

The API will be available at: **http://localhost:8080**

### API Documentation

- **Interactive API Documentation (Swagger):** http://localhost:8080/docs
- **Alternative Documentation (ReDoc):** http://localhost:8080/redoc

### API Endpoints

#### 1. **POST /visit** - Log a customer visit to promotion
Logs when a customer visits the promotion pages and returns the total visitor count for publicity display.

**Request Body:**
```json
{
  "user_id": "unique_customer_id",
  "page_url": "https://ecommerce.com/promotion",
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "referrer": "https://google.com"
}
```

**Response:**
```json
{
  "success": true,
  "visit_count": 1247,
  "message": "Visit logged successfully. Total visits: 1247"
}
```

**Example curl command:**
```bash
curl -X POST http://localhost:8080/visit \
  -H "Content-Type: application/json" \
  -d '{"user_id": "customer123", "page_url": "https://ecommerce.com/promotion"}'
```

#### 2. **GET /stats** - Get promotion campaign statistics  
Returns comprehensive statistics about the promotion campaign including visitor metrics and campaign performance.

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

#### Manual Testing

1. **Start the server:**
   ```bash
   poetry run python -m simple_api.run
   ```

2. **Test logging a promotion visit:**
   ```bash
   curl -X POST http://localhost:8080/visit \
     -H "Content-Type: application/json" \
     -d '{"user_id": "test_customer", "page_url": "https://ecommerce.com/promotion"}'
   ```

3. **Check promotion statistics:**
   ```bash
   # Default campaign stats (1 hour recent visitors)
   curl http://localhost:8080/stats
   
   # Custom timeframe stats (30 minutes recent visitors)
   curl "http://localhost:8080/stats?timeframe_hours=0.5"
   ```

#### Performance Testing

Load test the API with Locust:

```bash
# Install testing dependencies
pip install -r requirements.txt

# Start the API
make run

# Run load tests (separate terminal)
locust --host=http://localhost:8080
```

Then open http://localhost:8089 for the Locust web interface.

**Quick load tests:**
```bash
# Light load (10 users, 60 seconds)
locust --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 60s --headless

# Heavy load (100 users, 5 minutes)  
locust --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 300s --headless
```

See [README-TESTING.md](README-TESTING.md) and [TESTING.md](TESTING.md) for comprehensive testing documentation.

### Architecture Notes

- **Thread Safety:** Uses multiprocessing.Manager with locks to prevent race conditions during high-traffic promotion periods
- **MockedDB:** Simulates customer visit tracking database using shared memory objects
- **FastAPI:** Provides automatic API documentation and request validation for e-commerce integration
- **Pydantic:** Ensures type safety for customer visit data and promotion statistics
- **Campaign Analytics:** Real-time visitor counting and statistics for promotion publicity campaigns
- **Parameter Validation:** Automatically validates timeframe_hours range (0.1-168.0) for campaign reporting periods 