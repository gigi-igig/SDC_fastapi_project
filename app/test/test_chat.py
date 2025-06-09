import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from model.Interfaces import ChatRequest
from main import app
import httpx  # add this import

client = TestClient(app)

class MockResp:
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):  # Synchronous function
        return self._json_data

    # Asynchronous context manager for the mock response
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


# Successful chat response test
def test_chat_success_with_mock(monkeypatch):
    mock_response = MockResp(status_code=200, json_data={"message": {"role": "assistant", "content": "Hello!"}})
    
    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    payload = {
        "model": "phi3",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }
    response = client.post("/chat/", json=payload)

    assert response.status_code == 200
    assert response.json() == {"message": {"role": "assistant", "content": "Hello!"}}

# Test for model not found error
def test_chat_model_not_found(monkeypatch):
    mock_response = MockResp(status_code=400, json_data={"detail": "Model not found or not loaded."})

    async def mock_post(*args, **kwargs):
        return mock_response

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    payload = {
        "model": "ohter_model",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    }

    response = client.post("/chat/", json=payload)
    assert response.status_code == 400
    assert "Model not found" in response.json()["detail"]

# Test for server error (500)
def test_chat_server_error(monkeypatch):
    class MockResp:
        status_code = 500

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        def json(self):
            return {"detail": "Ollama server error."}

    async def mock_post(*args, **kwargs):
        return MockResp()

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    response = client.post("/chat/", json={
        "model": "phi3",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    })
    assert response.status_code == 500
    assert "server error" in response.json()["detail"].lower()

# Test for request error (connection error)
def test_chat_request_error(monkeypatch):
    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def post(self, *args, **kwargs):
            raise httpx.RequestError("Connection error")

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: MockAsyncClient())

    response = client.post("/chat/", json={
        "model": "phi3",
        "messages": [{"role": "user", "content": "Hi"}],
        "stream": False
    })

    assert response.status_code == 404
    assert "error communicating" in response.json()["detail"].lower()
