"""FastAPI OpenRouter LLM API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import ValidationError

from ...logging_utils import setup_logger
from ..models.requests import ChatCompletionRequest
from ..services.openrouter_service import OpenRouterService

openrouter_router = APIRouter(prefix="/openrouter", tags=["openrouter"])
logger: logging.Logger = setup_logger(__name__)


def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


@openrouter_router.post("/completions")
async def chat_completions(
    chat_request: ChatCompletionRequest, request: Request, request_id: str = Depends(get_request_id)
):
    """Chat completions endpoint.

    This endpoint generates a chat completion based on the provided prompt and parameters.

    Args:
        chat_request: A `ChatCompletionRequest` object containing the following fields:
            - `model` (str): Model to use for completion. Defaults to "google/gemini-2.5-pro".
            - `messages` (list[dict[str, Any]]): List of messages, must not be empty.
            - `api_key` (str): Your OpenRouter API key.
            - `max_tokens` (int, optional): Maximum tokens to generate.
            - `temperature` (float, optional): Sampling temperature (0.0-2.0).
            - `top_p` (float, optional): Nucleus sampling parameter (0.0-1.0).
            - `frequency_penalty` (float, optional): Frequency penalty (-2.0-2.0).
            - `presence_penalty` (float, optional): Presence penalty (-2.0-2.0).
            - `stream` (bool): Whether to stream responses. Defaults to False.
            - `site_url` (str, optional): Site URL for HTTP-Referer header.
            - `site_name` (str, optional): Site name for X-Title header.
        request: The incoming FastAPI request.
        request_id: The unique ID for the request.

    Returns:
        A JSON response with the chat completion.

    Raises:
        HTTPException: If the request is invalid or the OpenRouter API request fails.
    """
    try:
        logger.info(f"[{request_id}] Processing chat completion request")

        # Process request
        service = OpenRouterService()
        response, success = await service.chat_completion(chat_request, request_id)

        if not success:
            logger.error(f"[{request_id}] OpenRouter API request failed")
            raise HTTPException(status_code=502, detail="OpenRouter API request failed")

        logger.info(f"[{request_id}] Chat completion completed successfully")
        return response.model_dump()

    except ValidationError as e:
        logger.error(f"[{request_id}] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[{request_id}] Error in chat completions endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@openrouter_router.get("/models")
async def list_models(request: Request, request_id: str = Depends(get_request_id)):
    """List available models endpoint.

    This endpoint retrieves and lists all available models from the OpenRouter API.

    Args:
        request: The incoming FastAPI request.
        request_id: The unique ID for the request.

    Returns:
        A JSON response containing a list of available models.

    Raises:
        HTTPException: If the request fails or the OpenRouter API request fails.
    """
    try:
        logger.info(f"[{request_id}] Fetching available models")

        # Process request
        service = OpenRouterService()
        response, success = await service.list_models(request_id)

        if not success:
            logger.error(f"[{request_id}] Failed to fetch models")
            raise HTTPException(status_code=502, detail="Failed to fetch models from OpenRouter API")

        logger.info(f"[{request_id}] Models fetched successfully")
        return response.model_dump()

    except Exception as e:
        logger.error(f"[{request_id}] Error in models endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
