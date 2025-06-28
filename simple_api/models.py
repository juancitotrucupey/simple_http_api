"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class BuyRequest(BaseModel):
    """Request model for logging a buy"""
    user_id: int = Field(..., description="User ID")
    promotion_id: int = Field(..., description="Promotion ID")
    product_id: int = Field(..., description="Product ID")
    product_quantity: int = Field(..., description="Quantity of products purchased", gt=0)


class BuyInformation(BaseModel):
    """Internal model for storing buy information"""
    user_id: int = Field(..., description="User ID")
    promotion_id: int = Field(..., description="Promotion ID")  
    product_id: int = Field(..., description="Product ID")
    product_quantity: int = Field(..., description="Quantity of products purchased", gt=0)
    ip_address: str = Field(..., description="IP address of the client")
    timestamp: datetime = Field(..., description="Timestamp when the buy was made")


class BuyResponse(BaseModel):
    """Response model for buy logging"""
    success: bool = Field(..., description="Whether the buy was logged successfully")
    buy_count: int = Field(..., description="Total number of buys logged")
    message: str = Field(..., description="Response message")


class StatsRequest(BaseModel):
    """Model for statistics request parameters."""

    timeframe_hours: float = Field(
        default=1.0,
        ge=0.1,
        le=168.0,  # Maximum 1 week
        description="Timeframe in hours for recent visits (default: 1 hour, max: 168 hours/1 week)",
    )


class StatsResponse(BaseModel):
    """Response model for stats endpoint"""
    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    uptime_formatted: str = Field(..., description="Formatted uptime string") 
    total_buys: int = Field(..., description="Total number of buys")
    current_time: str = Field(..., description="Current server time")
    server_status: str = Field(..., description="Server status")
    n_recent_buys: int = Field(..., description="Number of recent buys")
    timeframe_hours: float = Field(..., description="Timeframe for recent buys in hours")


class HealthResponse(BaseModel):
    """Response model for health endpoint"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    uptime_seconds: float = Field(..., description="Server uptime in seconds")


class RootResponse(BaseModel):
    """Response model for root endpoint"""
    message: str = Field(..., description="Welcome message")
    version: str = Field(..., description="API version")
    endpoints: dict = Field(..., description="Available endpoints")
