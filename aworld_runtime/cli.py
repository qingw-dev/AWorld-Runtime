import logging
import time
import uuid

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
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


def main() -> None:
    """Run the FastAPI application using Uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "aworld_runtime.cli:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
        log_level=settings.log_level.lower(),
        timeout_keep_alive=1200,  # 20 minutes for agentic tasks
    )


if __name__ == "__main__":
    main()
