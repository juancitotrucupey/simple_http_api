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
        workers=n_workers
    )


def main() -> None:
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Start the Traffic Tracker API server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                           # Default: 4 workers, dev mode off, uvicorn
  python run.py --dev                     # Development mode with reload (1 worker)
  python run.py --n-workers 8            # 8 workers, dev mode off
  python run.py --dev --n-workers 1      # Development mode with explicit 1 worker
  python run.py --fastapi-cli             # Use FastAPI CLI instead of uvicorn
  python run.py --fastapi-cli --dev       # FastAPI CLI with reload (1 worker)
        """
    )
    
    parser.add_argument(
        "--n-workers",
        type=int,
        default=4,
        help="Number of worker processes (default: 4, auto-adjusts to 1 in dev mode). Must be 1 when --dev is used due to reload incompatibility"
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
    
    # Set n_workers to 1 when dev mode is enabled and n_workers wasn't explicitly set
    if args.dev and args.n_workers == 4:  # 4 is the default value
        args.n_workers = 1
    
    # Validate n_workers when in development mode
    if args.dev and args.n_workers != 1:
        raise ValueError(
            f"❌ Invalid configuration: n_workers must be 1 when dev mode is enabled.\n"
            f"   Current values: n_workers={args.n_workers}, dev={args.dev}\n"
            f"   \n"
            f"   Reason: Development mode with auto-reload is incompatible with multiple workers\n"
            f"   because the reload mechanism can't properly coordinate across multiple processes.\n"
            f"   \n"
            f"   Solutions:\n"
            f"   1. Use dev mode with 1 worker: --dev --n-workers 1\n"
            f"   2. Use dev mode without specifying workers: --dev (defaults to 1)\n"
            f"   3. Use multiple workers without dev mode: --n-workers {args.n_workers}\n"
            f"   4. For production with multiple workers: --n-workers {args.n_workers} (no --dev flag)"
        )
    
    if args.fastapi_cli:
        run_with_fastapi_cli(args.n_workers, args.dev)
    else:
        run_with_uvicorn(args.n_workers, args.dev)


if __name__ == "__main__":
    main()
