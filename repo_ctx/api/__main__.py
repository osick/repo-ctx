"""Entry point for running the API server as a module.

Usage:
    uv run python -m repo_ctx.api
    uv run python -m repo_ctx.api --host 0.0.0.0 --port 8080
"""

import argparse
import uvicorn


def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description="repo-ctx API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")

    args = parser.parse_args()

    uvicorn.run(
        "repo_ctx.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )


if __name__ == "__main__":
    main()
