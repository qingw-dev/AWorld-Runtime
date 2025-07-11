import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the FastAPI application."""
    # Startup logic here
    yield
    # Shutdown logic here


app = FastAPI(
    title="AWorld GAIA",
    description="GAIA (General AI Assistant) is the AWorld's brain, providing the ability to understand and perform tasks.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    """Root endpoint for the GAIA API."""
    return {"message": "Welcome to GAIA API"}


# Placeholder for exposing MCP server for all collections
# We will dynamically discover and load all ActionCollection subclasses


async def main():
    """Main function to run the FastAPI server."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    asyncio.run(main())
