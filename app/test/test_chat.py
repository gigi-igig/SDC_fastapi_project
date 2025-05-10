import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from dependencies.SessionData import get_session_service
import json

@pytest.fixture
def client():
    return TestClient(app)

#  正常回應
def test_chat_with_valid_input(client: TestClient):
    payload = {
        "model": "phi3",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    # 建立假的 session service，回傳 None 模擬不存在的 session
    class FakeSessionService:
        def read_single_session(self, session_id):
            return None

    # 使用 dependency_overrides 來覆寫依賴
    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    response = client.post("/chat/?session_id=9999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Session ID not found."}

    # 清除依賴覆寫，避免影響其他測試
    app.dependency_overrides.clear()


#  session_id 不存在
def test_chat_with_invalid_session_id(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    response = client.post("/chat/?session_id=9999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


#  歷史消息無法解析
def test_chat_with_invalid_history(client: TestClient):
    payload = {
        "model": "test-model",
        "messages": [{"role": "user", "content": "What's up?"}],
        "stream": False
    }

    # 建立模擬 SessionService 與回傳值
    mock_service = AsyncMock()
    mock_session = AsyncMock()
    mock_session.messages = "not a json string"
    mock_service.read_single_session.return_value = mock_session

    # 使用 dependency_overrides 來 mock get_session_service
    app.dependency_overrides[get_session_service] = lambda: mock_service

    client = TestClient(app)
    response = client.post("/chat/?session_id=123", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to parse session messages."}


    # 清除覆寫
    app.dependency_overrides.clear()


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
def test_chat_with_stream(client):
    payload = {
        "model": "phi3",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True
    }

    # 建立假的 session service，模擬依賴
    class FakeSessionService:
        def read_single_session(self, session_id):
            return None  # 沒有歷史訊息

        def update_messages(self, session_id, messages):
            pass
    
    # 使用 async generator 模擬非同步串流回應
    async def fake_aiter_lines():
        yield 'data: {"role": "assistant", "content": "Hello there!"}'

    # 模擬 httpx.AsyncClient.post 回傳的 response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.aiter_lines = fake_aiter_lines

    # 替代依賴
    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        with client.stream("POST", "/chat/", json=payload) as response:
            assert response.status_code == 200
            chunks = list(response.iter_text())
            print("Chunks:", chunks)
            assert any("Hello" in chunk for chunk in chunks)

    # 清除依賴覆蓋
    app.dependency_overrides.clear()