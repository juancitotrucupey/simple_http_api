"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class BuyRequest(BaseModel):
    """Model for buy request."""

    user_id: int = Field(..., description="Unique identifier for the user")
    promotion_id: int = Field(..., description="Unique identifier for the promotion")
    product_id: int = Field(..., description="Unique identifier for the product")
    product_amount: float = Field(..., description="Amount of the product")
    

class BuyInformation(BaseModel):
    """Model for internal buy information storage."""

    user_id: int = Field(..., description="Unique identifier for the user")
    promotion_id: int = Field(..., description="Unique identifier for the promotion")
    product_id: int = Field(..., description="Unique identifier for the product")
    product_amount: float = Field(..., description="Amount of the product")
    ip_address: str = Field(..., description="Client IP address")
    timestamp: datetime = Field(..., description="Request generation timestamp")

class BuyResponse(BaseModel):
    """Model for buy logging response."""

    success: bool = Field(..., description="Whether the visit was logged successfully")
    buy_count: int = Field(..., description="Total number of buys")
    message: str = Field(..., description="Response message for the user")

class StatsRequest(BaseModel):
    """Model for statistics request parameters."""

    timeframe_hours: float = Field(
        default=1.0,
        ge=0.1,
        le=168.0,  # Maximum 1 week
        description="Timeframe in hours for recent visits (default: 1 hour, max: 168 hours/1 week)",
    )


class StatsResponse(BaseModel):
    """Model for statistics response."""

    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    uptime_formatted: str = Field(..., description="Human-readable uptime")
    total_buys: int = Field(..., description="Total number of buys logged")
    current_time: datetime = Field(..., description="Current server time")
    server_status: str = Field(..., description="Server status")
    n_recent_buys: int = Field(..., description="Number of buys in the specified timeframe")
    timeframe_hours: float = Field(..., description="Timeframe used for recent buys calculation")
