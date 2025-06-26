"""Main FastAPI application for traffic tracking."""

import time
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from simple_api.database import MockedDB
from simple_api.models import StatsRequest, StatsResponse, VisitRequest, VisitResponse

# Initialize FastAPI app
app = FastAPI(
    title="Traffic Tracker API",
    description="Basic example of a traffic tracker for a website",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize mocked database
db = MockedDB()

# Track server start time for uptime calculation
SERVER_START_TIME = time.time()


def get_stats_request(timeframe_hours: float = 1.0) -> StatsRequest:
    """Dependency to create StatsRequest from query parameters with validation."""
    try:
        return StatsRequest(timeframe_hours=timeframe_hours)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


def format_uptime(uptime_seconds: float) -> str:
    """Format uptime seconds into human-readable string."""
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m {seconds}s"
    elif hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint providing basic API information."""
    return {
        "message": "Traffic Tracker API",
        "version": "0.1.0",
        "endpoints": {
            "POST /visit": "Log a user visit",
            "GET /stats": "Get server statistics",
            "GET /docs": "API documentation",
        },
    }


@app.post("/visit", response_model=VisitResponse, summary="Log a user visit")
async def log_visit(visit_data: VisitRequest, request: Request) -> VisitResponse:
    """
    Log a user visit to the website.

    This endpoint accepts user visit information, stores it in the database,
    and returns the updated visit count. The operation is thread-safe using
    multiprocessing locks to prevent race conditions.

    Args:
        visit_data: Visit information including user_id, page_url, etc.
        request: FastAPI request object for extracting client info

    Returns:
        VisitResponse: Success status, visit count, and message
    """
    try:
        # Extract client IP if not provided
        if not visit_data.ip_address:
            visit_data.ip_address = request.client.host if request.client else "unknown"

        # Add visit to database (thread-safe operation)
        total_visits = db.add_page_visit(visit_data)

        return VisitResponse(
            success=True, visit_count=total_visits, message=f"Visit logged successfully. Total visits: {total_visits}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log visit: {str(e)}") from e


@app.get("/stats", response_model=StatsResponse, summary="Get server statistics")
async def get_stats(stats_request: StatsRequest = Depends(get_stats_request)) -> StatsResponse:  # noqa: B008
    """
    Get comprehensive server statistics.

    Returns information about server uptime, total visits, current time,
    and other relevant metrics for monitoring the traffic tracker service.

    Args:
        stats_request: Request parameters including timeframe for recent visits calculation

    Returns:
        StatsResponse: Complete server statistics
    """
    try:
        current_time = time.time()
        uptime_seconds = current_time - SERVER_START_TIME

        # Get visit statistics from database
        total_visits = db.get_total_visits()
        recent_visits = db.get_recent_visits(hours=stats_request.timeframe_hours)

        return StatsResponse(
            uptime_seconds=uptime_seconds,
            uptime_formatted=format_uptime(uptime_seconds),
            total_visits=total_visits,
            current_time=datetime.now(),
            server_status="running",
            recent_visits=recent_visits,
            timeframe_hours=stats_request.timeframe_hours,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve statistics: {str(e)}") from e


@app.get("/health", summary="Health check endpoint")
async def health_check() -> dict[str, str | float]:
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - SERVER_START_TIME,
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 errors with custom response."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested path '{request.url.path}' was not found",
            "available_endpoints": ["/", "/visit", "/stats", "/health", "/docs"],
        },
    )


# Server can be started using: python -m simple_api.run
