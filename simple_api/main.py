"""Main FastAPI application for tracking purchases in an e-commerce website."""

import time
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from simple_api.database import MockedDB
from simple_api.models import StatsRequest, StatsResponse, BuyRequest, BuyResponse, BuyInformation
from simple_api.utils import extract_client_ip, format_uptime, get_stats_request, get_request_generation_time

# Initialize FastAPI app
app = FastAPI(
    title="Purchase Tracker API",
    description="Basic example of a purchase tracker for an e-commerce website",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize mocked database
db = MockedDB()

# Track server start time for uptime calculation
SERVER_START_TIME = time.time()


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


@app.post("/buy", response_model=BuyResponse, summary="Log a user buy")
async def log_buy(buy_data: BuyRequest, request: Request) -> BuyResponse:
    """
    Log a user purchase to the website.

    This endpoint accepts user purchase information, stores it in the database,
    and returns the updated purchase count. The operation is thread-safe using
    multiprocessing locks to prevent race conditions.

    Automatically extracts and enriches request data with:
    - Real client IP address (handling proxies and load balancers)
    - Request generation/timing information from headers

    Args:
        buy_data: Buy information including user_id, promotion_id, product_id, product_quantity
        request: FastAPI request object for extracting client info

    Returns:
        BuyResponse: Success status, buy count, and timing information
    """
    
    # Extract and enhance client information
    client_ip = extract_client_ip(request)
    
    request_generation_time = get_request_generation_time(request)

    buy_information = {
        "user_id": buy_data.user_id,
        "promotion_id": buy_data.promotion_id,
        "product_id": buy_data.product_id,
        "product_quantity": buy_data.product_quantity,
        "ip_address": client_ip,
        "timestamp": request_generation_time,
    }
    
    # Add buy to database (thread-safe operation)
    total_buys = db.add_product_buy(BuyInformation(**buy_information))

    return BuyResponse(
        success=True,
        buy_count=total_buys,
        message=f"Buy logged successfully. Total buys: {total_buys}",
    )


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
        current_time = datetime.now()
        uptime_seconds = (time.time() - SERVER_START_TIME)

        # Get buy statistics from database
        total_buys = db.get_total_buys()
        n_recent_buys = db.get_recent_buys(hours=stats_request.timeframe_hours)

        return StatsResponse(
            uptime_seconds=uptime_seconds,
            uptime_formatted=format_uptime(uptime_seconds),
            total_buys=total_buys,
            current_time=current_time.isoformat(),
            server_status="healthy",
            n_recent_buys=n_recent_buys,
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
            "available_endpoints": ["/", "/buy", "/stats", "/health", "/docs"],
        },
    )