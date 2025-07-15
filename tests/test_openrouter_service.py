import pytest
from aioresponses import aioresponses

from aworld_runtime.openrouter.models.requests import ChatCompletionRequest
from aworld_runtime.openrouter.services.openrouter_service import OpenRouterService


@pytest.mark.asyncio
async def test_chat_completion_success():
    """Test successful chat completion."""
    with aioresponses() as m:
        # Mock the chat completion endpoint
        response_data = {
            "id": "test_id",
            "choices": [{"message": {"content": "Hello response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        m.post(
            "https://openrouter.ai/api/v1/chat/completions",
            payload=response_data,
            status=200,
        )

        service = OpenRouterService()
        request_data = ChatCompletionRequest(
            model="test_model",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="test_key",
        )
        response, success = await service.chat_completion(request_data, "test_req_id")

        assert success is True
        assert response is not None
        assert response.response["id"] == "test_id"
        assert response.model == "test_model"


@pytest.mark.asyncio
async def test_list_models_success():
    """Test successful model listing."""
    with aioresponses() as m:
        # Mock the models endpoint
        models_data = {
            "data": [
                {"id": "model1", "name": "Test Model 1"},
                {"id": "model2", "name": "Test Model 2"},
            ]
        }
        m.get("https://openrouter.ai/api/v1/models", payload=models_data, status=200)

        service = OpenRouterService()
        response, success = await service.list_models("test_req_id")

        assert success is True
        assert response is not None
        assert len(response.models["data"]) == 2
        assert response.count == 2


@pytest.mark.asyncio
async def test_chat_completion_api_error():
    """Test chat completion with API error."""
    with aioresponses() as m:
        # Mock an API error
        m.post(
            "https://openrouter.ai/api/v1/chat/completions",
            status=400,
            payload={"error": "Bad request"},
        )

        service = OpenRouterService()
        request_data = ChatCompletionRequest(
            model="test_model",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="test_key",
        )
        response, success = await service.chat_completion(request_data, "test_req_id")

        assert success is False
        assert response is None


@pytest.mark.asyncio
async def test_list_models_api_error():
    """Test list models with API error."""
    with aioresponses() as m:
        # Mock an API error
        m.get(
            "https://openrouter.ai/api/v1/models",
            status=500,
            payload={"error": "Internal server error"},
        )

        service = OpenRouterService()
        response, success = await service.list_models("test_req_id")

        assert success is False
        assert response is None
