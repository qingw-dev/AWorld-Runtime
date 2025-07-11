import logging
import time
import uuid

import typer
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .gaia.services.sse_server import sse_cli as gaia_sse_cli
from .logging_utils import setup_logger
from .openrouter import openrouter_router

# Initialize logger
logger: logging.Logger = setup_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Search Server API",
        description="High-performance search and RAG API",
        version="1.0.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )

    # Include modular routers
    app.include_router(openrouter_router)

    # Add request processing middleware
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        """Add a unique request ID and log request details."""
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start_time = time.time()
        response: Response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Time: {process_time:.3f}s - "
            f"IP: {request.client.host}"
        )

        # Add custom headers to the response
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response

    return app


app = create_app()
cli = typer.Typer()


@cli.command()
def start_server(
    host: str = typer.Option("0.0.0.0", help="Server host"),
    port: int = typer.Option(19090, help="Server port"),
    debug: bool = typer.Option(False, help="Debug mode"),
    workers: int = typer.Option(4, help="Number of worker processes"),
    log_level: str = typer.Option("info", help="Logging level"),
):
    """Run the FastAPI application using Uvicorn."""
    uvicorn.run(
        "aworld_runtime.cli:app",
        host=host,
        port=port,
        reload=debug,
        workers=1 if debug else workers,
        log_level=log_level.lower(),
        timeout_keep_alive=1200,  # 20 minutes for agentic tasks
    )


@cli.command()
def gaia_mcp(
    name: str = typer.Option("gaia-mcp-server", help="Server name"),
    transport: str = typer.Option("stdio", help="Transport type (stdio or sse)"),
    port: int | None = typer.Option(None, help="Server port for SSE transport"),
    workspace: str | None = typer.Option(None, help="Workspace directory"),
    unittest: bool = typer.Option(False, help="Run in unittest mode"),
):
    """Run the GAIA MCP server."""
    if transport == "sse" and port is None:
        raise typer.BadParameter("--port is required when --transport=sse")
    if transport == "stdio" and port is not None:
        raise typer.BadParameter("--port should not be specified when --transport=stdio")

    # This is a bit of a hack to make it work with the existing sse_cli
    import sys

    sys.argv = ["aw-runtime", "--name", name, "--transport", transport]
    if port:
        sys.argv.extend(["--port", str(port)])
    if workspace:
        sys.argv.extend(["--workspace", workspace])
    if unittest:
        sys.argv.append("--unittest")

    gaia_sse_cli()


def main():
    cli()


if __name__ == "__main__":
    main()
