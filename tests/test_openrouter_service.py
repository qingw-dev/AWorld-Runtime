import pytest
from unittest.mock import AsyncMock, patch

from aworld_runtime.openrouter.services.openrouter_service import OpenRouterService
from aworld_runtime.openrouter.models.requests import ChatCompletionRequest

@pytest.mark.asyncio
async def test_chat_completion_success():
    """Test successful chat completion."""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"id": "test_id", "choices": []}
        mock_session.return_value.__aenter__.return_value.post.return_value = mock_response

        service = OpenRouterService()
        request_data = ChatCompletionRequest(
            model="test_model",
            messages=[{"role": "user", "content": "Hello"}],
            api_key="test_key"
        )
        response, success = await service.chat_completion(request_data, "test_req_id")

        assert success is True
        assert response is not None
        assert response.id == "test_id"

@pytest.mark.asyncio
async def test_list_models_success():
    """Test successful model listing."""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"data": []}
        mock_session.return_value.__aenter__.return_value.get.return_value = mock_response

        service = OpenRouterService()
        response, success = await service.list_models("test_req_id")

        assert success is True
        assert response is not None
        assert response.data == []