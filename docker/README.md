# Docker Setup for Simple HTTP API

This directory contains Docker configuration files for containerizing the Simple HTTP API with multiprocessing support.

## Files

- `Dockerfile` - Production-ready Docker build configuration with Poetry
- `docker-compose.yml` - Docker Compose configuration for easy deployment
- `.dockerignore` - Excludes unnecessary files from build context
- `README.md` - This documentation file

## Building and Running

### Using Docker Compose (Recommended)

```bash
# Build and run the container
cd docker
docker compose up --build

# Run in detached mode
docker compose up -d --build

# View logs
docker compose logs -f simple-api

# Stop the container
docker compose down
```

### Using Docker directly

```bash
# Build the image
docker build -f docker/Dockerfile -t simple-http-api .

# Run the container
docker run -p 8080:8080 simple-http-api

# Run in detached mode
docker run -d -p 8080:8080 --name simple-api simple-http-api
```

## Configuration

### Environment Variables

The Dockerfile sets the following environment variables for optimal performance:

**Python Configuration:**
- `PYTHONUNBUFFERED=1` - Ensures Python output is sent straight to terminal (essential for Docker logs)
- `PYTHONDONTWRITEBYTECODE=1` - Prevents Python from writing .pyc files (reduces image size)
- `PIP_NO_CACHE_DIR=1` - Disables pip cache (reduces image size)
- `PIP_DISABLE_PIP_VERSION_CHECK=1` - Speeds up pip operations

**Poetry Configuration:**
- `POETRY_NO_INTERACTION=1` - Disables Poetry interactive prompts (essential for automated builds)
- `POETRY_VIRTUALENVS_CREATE=false` - Installs packages to system Python (essential for containers)
- `POETRY_CACHE_DIR=/tmp/poetry_cache` - Sets cache location for cleanup

### Default Configuration

- **Workers**: 1 worker process (required for proper mocked database functionality)
- **Port**: Application runs on port `8080`
- **Server**: Uvicorn ASGI server with configurable multiprocessing support
- **Mode**: Production mode (no auto-reload)

## Accessing the Application

Once running, the API will be available at:
- **API**: http://localhost:8080
- **Documentation**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health
- **Stats**: http://localhost:8080/stats

## Multiprocessing & Performance

### Default Configuration

The container uses **1 worker process** by default for compatibility with the mocked database implementation:
```dockerfile
CMD ["sh", "-c", "make run ARGS='--n-workers 1'"]
```

### Database Considerations

⚠️ **Important**: The application uses a mocked in-memory database with multiprocessing locks:
- **1 worker**: ✅ Thread-safe operation, shared memory works correctly
- **Multiple workers**: ❌ Each process has separate memory space, data not shared

### Customization Options

You can override the default configuration in several ways:

#### 1. **Override CMD in docker-compose.yml**

```yaml
services:
  simple-api:
    # Single worker (default, recommended)
    command: ["sh", "-c", "make run ARGS='--n-workers 1'"]
    
    # Development mode with auto-reload
    command: ["sh", "-c", "make run ARGS='--dev'"]
    
    # Multiple workers (only if using real database)
    command: ["sh", "-c", "make run ARGS='--n-workers 4'"]
    
    # FastAPI CLI mode
    command: ["sh", "-c", "make run ARGS='--fastapi-cli --n-workers 1'"]
```

#### 2. **Using Direct Poetry Commands**

```yaml
services:
  simple-api:
    # Direct uvicorn execution
    command: ["poetry", "run", "python", "-m", "simple_api.run", "--n-workers", "1"]
    
    # Development mode
    command: ["poetry", "run", "python", "-m", "simple_api.run", "--dev"]
    
    # FastAPI CLI
    command: ["poetry", "run", "python", "-m", "simple_api.run", "--fastapi-cli", "--dev"]
```

#### 3. **Development Setup with Live Reload**

```yaml
services:
  simple-api:
    command: ["sh", "-c", "make run ARGS='--dev'"]
    volumes:
      - ../simple_api:/app/simple_api  # Mount source code
    ports:
      - "8080:8080"
```

### Configuration Validation

The application includes smart validation:
- ✅ `--dev` automatically uses 1 worker
- ✅ `--dev --n-workers 1` is valid
- ❌ `--dev --n-workers 4` raises detailed error with solutions

### Performance Notes

**For Real Database Deployments:**
- Use multiple workers (`--n-workers 4` or higher)
- Disable development mode for production
- Consider using FastAPI CLI for advanced features

## Building from Scratch

### Clean Docker Cache

To force a complete rebuild without cache:

```bash
# Clean all Docker cache
docker system prune -a -f

# Clean only build cache
docker builder prune -f

# Build without cache
docker build --no-cache -f docker/Dockerfile -t simple-http-api .

# Docker Compose without cache
docker compose build --no-cache
```

### Complete Rebuild Process

```bash
# Remove existing containers and images
docker compose down --rmi all -v

# Clean cache and rebuild
docker builder prune -f
docker compose build --no-cache
docker compose up -d
```

## Troubleshooting

### Container won't start
- Check logs: `docker compose logs simple-api`
- Verify port 8080 is available: `lsof -i :8080`
- Ensure all required files are copied correctly
- Check if Poetry installation succeeded

### Build fails
- Make sure you're running from the project root directory
- Check that `pyproject.toml` and `poetry.lock` exist
- Verify Docker has enough disk space: `docker system df`
- Try building without cache: `docker build --no-cache`

### Package import errors
- Ensure `POETRY_VIRTUALENVS_CREATE=false` is set
- Verify Poetry cache cleanup doesn't remove packages
- Check that dependencies are installed with `--only=main`

### Performance issues
- For mocked database: Use only 1 worker (`--n-workers 1`)
- For real database: Use multiple workers (`--n-workers 4+`)
- Monitor with: `docker stats simple-api`

### Development mode issues
- Ensure volume mounts are correct for live reload
- Use `--dev` flag for auto-reload functionality
- Check that only 1 worker is used in development mode

### Command validation errors
- Review error message for specific solutions
- Use `--dev --n-workers 1` or just `--dev`
- For production: avoid `--dev` flag entirely

## Quick Reference

### Common Commands

```bash
# Build and run with default settings (1 worker)
docker compose up --build

# Development mode with auto-reload
docker compose run --rm simple-api sh -c "make run ARGS='--dev'"

# Custom worker count (for real database)
docker compose run --rm simple-api sh -c "make run ARGS='--n-workers 4'"

# Interactive shell for debugging
docker compose run --rm simple-api bash

# Check application logs
docker compose logs -f simple-api

# Test API endpoints
curl http://localhost:8080/health
curl http://localhost:8080/stats
curl -X POST http://localhost:8080/visit -H "Content-Type: application/json" -d '{"user_id": "test", "page_url": "http://example.com"}'
```

### Environment Comparison

| Environment | Workers | Reload | Command |
|-------------|---------|--------|---------|
| **Development** | 1 | ✅ Yes | `make run ARGS='--dev'` |
| **Testing** | 1 | ❌ No | `make run ARGS='--n-workers 1'` |  
| **Production (Mocked DB)** | 1 | ❌ No | `make run ARGS='--n-workers 1'` |
| **Production (Real DB)** | 4+ | ❌ No | `make run ARGS='--n-workers 4'` |

### Key Features

- ✅ **Multiprocessing Support**: Configurable worker processes
- ✅ **Development Mode**: Auto-reload with `--dev` flag  
- ✅ **FastAPI CLI Integration**: Modern FastAPI tooling
- ✅ **Smart Validation**: Prevents invalid configurations
- ✅ **Optimized Docker**: Minimal image size with Poetry
- ✅ **Thread-Safe Database**: Mocked database with multiprocessing locks 