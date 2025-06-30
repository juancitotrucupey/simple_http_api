# E-commerce Promotion Buy Tracker API

**FastAPI-based system for tracking user purchases during e-commerce promotion campaigns.** This API records customer buy transactions on promotional pages and provides analytics data to measure promotion effectiveness and customer engagement.

## 📋 Technical Report

**[📑 Complete Technical Analysis](technical_report.md)** - Comprehensive technical documentation covering:
- **Concurrency Strategy**: Thread-safety implementation and scalability considerations
- **Performance Analysis**: Detailed performance characteristics and bottleneck analysis  
- **Production Readiness**: Database migration roadmap and scaling architecture

*This report addresses technical evaluation criteria including concurrency handling, performance optimization, and production deployment strategy.*

---

## 🎯 Purpose

This API serves as a **buy tracking and analytics system** for e-commerce promotional campaigns:

- **📊 Purchase Analytics**: Track user purchases on promotional pages
- **🔍 Campaign Performance**: Monitor promotion effectiveness through buy metrics  
- **👥 User Behavior**: Analyze customer purchasing patterns
- **⏱️ Timing Analysis**: Extract request generation timestamps for accurate analytics
- **📈 Real-time Stats**: Provide live campaign performance data

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
   poetry install --no-root --extras dev
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
  - `main.py` - FastAPI application and endpoints
  - `models.py` - Pydantic data models
  - `database.py` - Mock database with thread-safe operations
  - `utils.py` - Utility functions (IP extraction, timestamp parsing)
  - `run.py` - Server startup script with configuration
- `docker/` - Docker configuration files
- `pyproject.toml` - Project configuration and dependencies
- `Makefile` - Development automation commands

## Running the API

### Starting the Server

The Buy Tracker API can be started in multiple ways, depending on your needs:

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

## 📋 API Endpoints

### 1. **POST /buy** - Log a customer purchase

**Purpose**: Records when a customer makes a purchase on a promotional page. This is the core endpoint for tracking buy transactions and building analytics data.

**Request Body:**
```json
{
  "user_id": 12345,
  "promotion_id": 67890,
  "product_id": 11111, 
  "product_quantity": 5
}
```

**Field Descriptions:**
- `user_id` (int): Unique identifier for the customer
- `promotion_id` (int): Unique identifier for the promotion campaign  
- `product_id` (int): Unique identifier for the purchased product
- `product_quantity` (int): Quantity of products purchased (must be positive)

**Response:**
```json
{
  "success": true,
  "buy_count": 1247,
  "message": "Buy logged successfully. Total buys: 1247"
}
```

**Advanced: Timestamp Headers**

The API supports extracting request generation time from various HTTP headers for accurate timing analytics:

**Client Timestamp Headers:**
- `x-timestamp`: ISO datetime string (`2025-06-27T20:14:12Z`)
- `x-client-time`: Unix timestamp in seconds 
- `x-request-time`: Custom request timing
- `timestamp`: Simple timestamp header

**Infrastructure Timing Headers:**
- `x-request-start`: Proxy/Load balancer timestamps (usually milliseconds)
- `x-queue-start`: Queue timing from services like Heroku (microseconds) 
- `x-request-received`: Custom proxy headers
- `x-forwarded-start`: Load balancer start time

**Example curl commands:**

**Basic purchase logging:**
```bash
curl -X POST http://localhost:8080/buy \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12345,
    "promotion_id": 67890,
    "product_id": 11111,
    "product_quantity": 5
  }'
```

**With client timestamp for accurate analytics:**
```bash
curl -X POST http://localhost:8080/buy \
  -H "Content-Type: application/json" \
  -H "x-timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -d '{
    "user_id": 12345,
    "promotion_id": 67890,
    "product_id": 11111,
    "product_quantity": 5
  }'
```

**With Unix timestamp:**
```bash  
curl -X POST http://localhost:8080/buy \
  -H "Content-Type: application/json" \
  -H "x-client-time: $(date +%s)" \
  -d '{
    "user_id": 12345,
    "promotion_id": 67890, 
    "product_id": 11111,
    "product_quantity": 5
  }'
```

### 2. **GET /stats** - Get promotion campaign analytics

**Purpose**: Returns comprehensive analytics about promotion performance including buy metrics, server uptime, and campaign statistics for decision-making.

**Query Parameters:**
- `timeframe_hours` (optional): Timeframe in hours for recent buys calculation
  - Default: `1.0` (1 hour)
  - Minimum: `0.1` (6 minutes) 
  - Maximum: `168.0` (1 week)

**Response:**
```json
{
  "uptime_seconds": 3600.5,
  "uptime_formatted": "1h 0m 0s", 
  "total_buys": 1247,
  "current_time": "2025-06-27T20:14:12.123456",
  "server_status": "healthy",
  "n_recent_buys": 45,
  "timeframe_hours": 1.0
}
```

**Field Descriptions:**
- `uptime_seconds`: Server uptime in seconds
- `uptime_formatted`: Human-readable uptime string
- `total_buys`: Total number of purchases recorded
- `current_time`: Current server timestamp
- `server_status`: Current server health status
- `n_recent_buys`: Number of purchases in the specified timeframe
- `timeframe_hours`: Timeframe used for recent buys calculation

**Example curl commands:**

**Default analytics (1 hour recent buys):**
```bash
curl http://localhost:8080/stats
```

**Custom timeframe (30 minutes recent buys):**
```bash
curl "http://localhost:8080/stats?timeframe_hours=0.5"
```

**Daily analytics (24 hours recent buys):**
```bash
curl "http://localhost:8080/stats?timeframe_hours=24.0"
```

**Weekly analytics (7 days recent buys):**
```bash
curl "http://localhost:8080/stats?timeframe_hours=168.0"
```

### 3. **GET /health** - Health check

**Purpose**: Simple health check endpoint for monitoring and load balancer health checks.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-27T20:14:12.123456",
  "uptime_seconds": 3600.5
}
```

**Example curl command:**
```bash
curl http://localhost:8080/health
```

### 4. **GET /** - API Information

**Purpose**: Root endpoint providing basic API information and available endpoints.

**Response:**
```json
{
  "message": "Traffic Tracker API",
  "version": "0.1.0",
  "endpoints": {
    "POST /buy": "Log a user purchase",
    "GET /stats": "Get server statistics", 
    "GET /docs": "API documentation"
  }
}
```

## 🧪 Testing the API

### Manual Testing

#### Manual Testing

1. **Start the server:**
   ```bash
   make run
   # Server available at http://localhost:8080
   ```

2. **Test logging a purchase:**
   ```bash
   curl -X POST http://localhost:8080/buy \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 12345,
       "promotion_id": 67890,
       "product_id": 11111,
       "product_quantity": 5
     }'
   ```

3. **Check campaign analytics:**
   ```bash
   # Recent buys (last hour)
   curl http://localhost:8080/stats
   
   # Recent buys (last 30 minutes)  
   curl "http://localhost:8080/stats?timeframe_hours=0.5"
   
   # Daily analytics
   curl "http://localhost:8080/stats?timeframe_hours=24.0"
   ```

4. **Verify server health:**
   ```bash
   curl http://localhost:8080/health
   ```

### Performance Testing

Load test the API with Locust for promotion campaign simulation:

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
# Light load (10 concurrent users, 60 seconds)
locust --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 60s --headless

# Heavy promotion traffic (100 concurrent users, 5 minutes)  
locust --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 300s --headless

# Stress test (500 concurrent users, 10 minutes)
locust --host=http://localhost:8080 --users 500 --spawn-rate 25 --run-time 600s --headless
```

#### 📊 Comprehensive Performance Analysis

For detailed performance analysis results including throughput metrics, response time characteristics, and breaking point analysis, see:

**[📋 Performance Analysis Report](performance_analysis/performance_analysis_report.md)**

This comprehensive report includes:
- **Performance characteristics** at different load levels (5-300 concurrent users)
- **Degradation points** and breaking point analysis  
- **Throughput analysis** and scaling factors
- **Production deployment recommendations**
- **Monitoring strategy** and SLA guidelines
- **Detailed test results** with HTML reports for each load scenario

## 🏗️ Architecture & Features

### Core Features

- **🔒 Thread Safety**: Uses multiprocessing.Manager with locks to prevent race conditions during high-traffic promotion periods
- **💾 MockedDB**: Simulates purchase tracking database using shared memory objects for development/testing
- **📝 Auto Documentation**: FastAPI provides automatic API documentation and request validation
- **✅ Type Safety**: Pydantic ensures type safety for purchase data and analytics responses
- **🌐 IP Detection**: Automatically extracts real client IPs handling proxies and load balancers
- **⏱️ Timestamp Extraction**: Advanced request timing analysis from HTTP headers
- **📊 Real-time Analytics**: Live buy counting and statistics for promotion campaigns
- **🔧 Parameter Validation**: Automatic validation of timeframe_hours range (0.1-168.0)

### Data Models

**BuyRequest** (Input):
```python
{
    "user_id": int,          # Customer identifier
    "promotion_id": int,     # Promotion campaign ID  
    "product_id": int,       # Product identifier
    "product_quantity": int  # Quantity of products purchased
}
```

**BuyInformation** (Internal Storage):
```python
{
    "user_id": int,
    "promotion_id": int,
    "product_id": int, 
    "product_quantity": int,
    "ip_address": str,       # Extracted client IP
    "timestamp": datetime    # Request generation time
}
```

**BuyResponse** (Output):
```python
{
    "success": bool,         # Operation success status
    "buy_count": int,        # Total buys recorded
    "message": str           # Human-readable response
}
```

### Error Handling

The API provides comprehensive error responses:

- **422 Unprocessable Entity**: Invalid request data (wrong types, missing fields)
- **500 Internal Server Error**: Server-side errors with detailed logging
- **404 Not Found**: Non-existent endpoints with helpful error messages

### Production Considerations

- **Multi-worker Setup**: Run with multiple workers for production traffic
- **Load Balancing**: API supports standard load balancer health checks
- **Monitoring**: Use `/health` endpoint for uptime monitoring
- **Analytics**: Use `/stats` endpoint for campaign performance tracking
- **Scaling**: Thread-safe design supports horizontal scaling

## 🐳 Docker Support

Docker configuration is available in the `docker/` directory for containerized deployment:

```bash
# Build and run with Docker Compose
docker compose -f docker/docker-compose.yml up --build

# API will be available at http://localhost:8080
```

## 📈 Use Cases

### E-commerce Promotion Analytics

1. **Campaign Performance Tracking**
   - Monitor real-time purchase activity
   - Track promotion effectiveness 
   - Analyze customer buying patterns

2. **Customer Behavior Analysis**
   - Identify high-value customers
   - Track product popularity
   - Monitor purchase timing patterns

3. **Business Intelligence**
   - Generate campaign reports
   - Calculate conversion rates
   - Optimize promotion strategies

### Integration Examples

**JavaScript Frontend Integration:**
```javascript
// Log a purchase
const logPurchase = async (userId, promotionId, productId, quantity) => {
  const response = await fetch('/buy', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-timestamp': new Date().toISOString()
    },
    body: JSON.stringify({
      user_id: userId,
      promotion_id: promotionId, 
      product_id: productId,
      product_quantity: quantity
    })
  });
  return response.json();
};

// Get campaign stats
const getCampaignStats = async (hours = 24) => {
  const response = await fetch(`/stats?timeframe_hours=${hours}`);
  return response.json();
};
```

**Python Client Integration:**
```python
import requests
from datetime import datetime

def log_purchase(user_id, promotion_id, product_id, quantity):
    """Log a customer purchase with timestamp"""
    url = "http://localhost:8080/buy"
    headers = {
        "Content-Type": "application/json",
        "x-timestamp": datetime.now().isoformat() + "Z"
    }
    data = {
        "user_id": user_id,
        "promotion_id": promotion_id,
        "product_id": product_id, 
        "product_quantity": quantity
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def get_campaign_analytics(timeframe_hours=24):
    """Get promotion campaign analytics"""
    url = f"http://localhost:8080/stats?timeframe_hours={timeframe_hours}"
    response = requests.get(url)
    return response.json()
``` 
