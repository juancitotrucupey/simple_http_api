"""
Utility functions for the Traffic Tracker API.

This module contains helper functions for IP extraction, formatting,
and request validation.
"""
from datetime import datetime
from fastapi import HTTPException, Request

from simple_api.models import StatsRequest

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


def extract_client_ip(request: Request) -> str:
    """
    Extract the real client IP address from the request.
    
    Handles various proxy scenarios and load balancers by checking headers
    in order of preference.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Client IP address or 'unknown' if not found
    """
    # Headers to check in order of preference for real client IP
    ip_headers = [
        "x-forwarded-for",      # Most common proxy header
        "x-real-ip",            # Nginx proxy header
        "cf-connecting-ip",     # Cloudflare
        "x-client-ip",          # Alternative client IP header
        "x-forwarded",          # Less common
        "forwarded-for",        # Alternative forwarded header
        "forwarded",            # RFC 7239 standard
    ]
    
    # Check proxy headers first
    for header in ip_headers:
        header_value = request.headers.get(header)
        if header_value:
            # Handle comma-separated IPs (x-forwarded-for can have multiple IPs)
            ip_list = [ip.strip() for ip in header_value.split(',')]
            for ip in ip_list:
                # Skip private/local IPs and get the first public IP
                if ip and not _is_private_ip(ip):
                    return ip
    
    # Fallback to direct client IP
    if request.client and request.client.host:
        client_ip = request.client.host
        return client_ip
    
    return "unknown"


def _is_private_ip(ip: str) -> bool:
    """
    Check if an IP address is private/local.
    
    Args:
        ip: IP address string
        
    Returns:
        bool: True if private IP, False otherwise
    """
    try:
        # Simple check for common private IP ranges
        if ip.startswith(("127.", "10.", "192.168.", "172.")):
            return True
        if ip.startswith("169.254."):  # Link-local
            return True
        if ip in ("localhost", "::1", "0.0.0.0"):
            return True
        return False
    except Exception:
        return True  # If we can't parse it, consider it private for safety

def get_request_generation_time(request: Request) -> datetime:
    """
    Extract request generation time from HTTP headers or use server receive time.
    
    Tries to extract timing information from various headers in order of preference:
    1. Client timestamp headers (x-timestamp, x-client-time, etc.)
    2. Infrastructure timing headers (x-request-start, x-queue-start, etc.)
    3. Falls back to server receive time
    
    All returned datetimes are timezone-naive (local time) for consistency.
    
    Args:
        request: FastAPI request object
        
    Returns:
        datetime: Request generation time (timezone-naive)
    """
    server_receive_time = datetime.now()  # Always timezone-naive
    
    # 1. Check for custom client timestamp headers
    client_time_headers = [
        "x-timestamp",           # Custom timestamp header
        "x-client-time",         # Client-side generation time
        "x-request-time",        # Request generation time
        "timestamp",             # Simple timestamp header
    ]
    
    for header in client_time_headers:
        header_value = request.headers.get(header.lower())
        if header_value:
            try:
                # Try parsing as ISO format first
                if 'T' in header_value or '-' in header_value:
                    # Handle timezone-aware timestamps by converting to naive
                    parsed_time = datetime.fromisoformat(header_value.replace('Z', '+00:00'))
                    # Convert to naive datetime (remove timezone info)
                    if parsed_time.tzinfo is not None:
                        parsed_time = parsed_time.replace(tzinfo=None)
                    
                    return parsed_time
                else:
                    # Try parsing as Unix timestamp
                    timestamp = float(header_value)
                    # Handle both seconds and milliseconds
                    if timestamp > 1e10:  # Likely milliseconds
                        timestamp = timestamp / 1000
                    parsed_time = datetime.fromtimestamp(timestamp)
                    
                    return parsed_time
                    
            except (ValueError, OSError) as e:
                continue
    
    # 2. Check for infrastructure/proxy timing headers
    proxy_time_headers = [
        "x-request-start",       # Nginx, HAProxy (usually milliseconds)
        "x-queue-start",         # Heroku (usually microseconds)
        "x-request-received",    # Custom proxy headers
        "x-forwarded-start",     # Some load balancers
    ]
    
    for header in proxy_time_headers:
        header_value = request.headers.get(header.lower())
        if header_value:
            try:
                timestamp = float(header_value)
                
                # Handle different time formats
                if timestamp > 1e12:  # Likely microseconds
                    timestamp = timestamp / 1_000_000
                elif timestamp > 1e10:  # Likely milliseconds
                    timestamp = timestamp / 1000
                
                parsed_time = datetime.fromtimestamp(timestamp)
                return parsed_time
                
            except (ValueError, OSError) as e:
                continue
    
    # 3. Fall back to server receive time
    return server_receive_time
    