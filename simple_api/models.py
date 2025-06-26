"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VisitRequest(BaseModel):
    """Model for visit logging request."""

    user_id: str = Field(..., description="Unique identifier for the user")
    page_url: str = Field(..., description="URL of the page being visited")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address of the visitor")
    referrer: Optional[str] = Field(None, description="Referrer URL")


class VisitResponse(BaseModel):
    """Model for visit logging response."""

    success: bool = Field(..., description="Whether the visit was logged successfully")
    visit_count: int = Field(..., description="Total number of visits")
    message: str = Field(..., description="Response message")


class StatsResponse(BaseModel):
    """Model for statistics response."""

    uptime_seconds: float = Field(..., description="Server uptime in seconds")
    uptime_formatted: str = Field(..., description="Human-readable uptime")
    total_visits: int = Field(..., description="Total number of visits logged")
    current_time: datetime = Field(..., description="Current server time")
    server_status: str = Field(..., description="Server status")
    recent_visits: int = Field(..., description="Number of visits in the last hour")
