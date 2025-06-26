"""Server startup script for the Traffic Tracker API."""

import argparse
import subprocess
import sys

import uvicorn


def run_with_fastapi_cli(n_workers: int, dev: bool) -> None:
    """Run the application using FastAPI CLI."""
    cmd = [
        "fastapi",
        "run",
        "--workers", str(n_workers),
        "--port", "8080",
        "simple_api/main.py"
    ]
    
    if dev:
        cmd.append("--reload")
    
    print("🚀 Starting Traffic Tracker API with FastAPI CLI...")
    print(f"📍 Server will be available at: http://localhost:8080")
    print(f"👥 Workers: {n_workers}")
    print(f"🔄 Development mode (reload): {dev}")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🔄 Interactive API: http://localhost:8080/redoc")
    print(f"🎯 Command: {' '.join(cmd)}")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server with FastAPI CLI: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ FastAPI CLI not found. Install it with: pip install 'fastapi[standard]'")
        sys.exit(1)


def run_with_uvicorn(n_workers: int, dev: bool) -> None:
    """Run the application using uvicorn directly."""
    print("🚀 Starting Traffic Tracker API with uvicorn...")
    print(f"📍 Server will be available at: http://localhost:8080")
    print(f"👥 Workers: {n_workers}")
    print(f"🔄 Development mode (reload): {dev}")
    print("📖 API Documentation: http://localhost:8080/docs")
    print("🔄 Interactive API: http://localhost:8080/redoc")
    print()

    uvicorn.run(
        "simple_api.main:app",
        host="0.0.0.0",
        port=8080,
        reload=dev,
        log_level="info",
        workers=n_workers if not dev else 1  # Workers > 1 incompatible with reload
    )


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Start the Traffic Tracker API server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                           # Default: 4 workers, dev mode off, uvicorn
  python run.py --dev                     # Development mode with reload
  python run.py --n-workers 8            # 8 workers, dev mode off
  python run.py --n-workers 2 --dev      # 2 workers, dev mode on
  python run.py --fastapi-cli             # Use FastAPI CLI instead of uvicorn
  python run.py --fastapi-cli --dev       # FastAPI CLI with reload
        """
    )
    
    parser.add_argument(
        "--n-workers",
        type=int,
        default=4,
        help="Number of worker processes (default: 4). Note: When dev=True, workers is set to 1 for uvicorn compatibility"
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Enable development mode with automatic reload on code changes"
    )
    
    parser.add_argument(
        "--fastapi-cli",
        action="store_true",
        help="Use FastAPI CLI instead of uvicorn directly"
    )
    
    args = parser.parse_args()
    
    if args.fastapi_cli:
        run_with_fastapi_cli(args.n_workers, args.dev)
    else:
        run_with_uvicorn(args.n_workers, args.dev)


if __name__ == "__main__":
    main()
