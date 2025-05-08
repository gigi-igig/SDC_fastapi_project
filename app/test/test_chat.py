import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import json

#  正常回應
def test_chat_with_valid_input(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"message": {"role": "assistant", "content": "I'm good!"}}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = client.post("/chat/", json=payload)

    assert response.status_code == 200
    assert response.json()["message"]["content"] == "I'm good!"


#  session_id 不存在
def test_chat_with_invalid_session_id(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    response = client.post("/chat/?session_id=9999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Session ID not found."}


#  歷史消息無法解析
def test_chat_with_invalid_history(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    mock_session = AsyncMock()
    mock_session.messages = "not a json string"

    with patch("dependencies.SessionData.SessionServiceDep.read_single_session", return_value=mock_session):
        response = client.post("/chat/?session_id=123", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to parse session messages."}


#  模型不存在
def test_chat_with_ollama_server_error(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    mock_response = AsyncMock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"detail": "Model not found or not loaded."}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = client.post("/chat/", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "Model not found or not loaded."}


#  Ollama 回傳 500
def test_chat_with_ollama_server_internal_error(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Ollama server error."}

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = client.post("/chat/", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Ollama server error."}


#  測試串流
def test_chat_with_stream(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": True
    }

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.aiter_lines.return_value = iter(['{"message": "Hello"}\n'])

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        response = client.post("/chat/", json=payload)

    assert response.status_code == 200
    assert b'{"message": "Hello"}' in response.content
