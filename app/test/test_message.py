import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from main import app  # 替換為你的應用主程式入口
from dependencies.MessageData import get_message_service
from dependencies.SessionData import get_session_service

# 測試資料
mock_message = {
    "id": 1,
    "content": "Hello",
    "role": "user"
}
mock_create_payload = {
    "content": "Hello",
    "session_id": 1,
    "role": "user"
}


@pytest.fixture
def client():
    return TestClient(app)


def override_services(session_exists=True):
    # Mock SessionService
    mock_session_service = MagicMock()
    mock_session_service.read_single_session.return_value = {"id": 1} if session_exists else None

    # Mock MessageService
    mock_message_service = MagicMock()
    mock_message_service.add_message.return_value = mock_message
    mock_message_service.get_messages.return_value = [mock_message]

    app.dependency_overrides[get_session_service] = lambda: mock_session_service
    app.dependency_overrides[get_message_service] = lambda: mock_message_service


def test_add_message_success(client):
    override_services(session_exists=True)
    response = client.post("/messages/", json=mock_create_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello"
    assert data["role"] == "user"
    assert data["id"] == 1


def test_add_message_session_not_found(client):
    override_services(session_exists=False)
    response = client.post("/messages/", json=mock_create_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Session ID not found."


def test_list_messages_success(client):
    override_services(session_exists=True)
    response = client.get("/messages/", params={"session_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["content"] == "Hello"


def test_list_messages_session_not_found(client):
    override_services(session_exists=False)
    response = client.get("/messages/", params={"session_id": 1})
    assert response.status_code == 404
    assert response.json()["detail"] == "Session ID not found."


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    yield
    app.dependency_overrides.clear()
