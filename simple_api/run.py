"""Server startup script for the Traffic Tracker API."""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Traffic Tracker API...")
    print("📍 Server will be available at: http://localhost:8080")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🔄 Interactive API: http://localhost:8080/redoc")

    uvicorn.run("simple_api.main:app", host="0.0.0.0", port=8080, reload=True, log_level="info")
