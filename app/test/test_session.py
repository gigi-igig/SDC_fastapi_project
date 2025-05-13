import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime

from main import app  # 或者你的 app 實例
from dependencies.SessionData import get_session_service
from model.Interfaces import CreateSessionRequest
from types import SimpleNamespace

client = TestClient(app)

# 建立假的 SessionService 實作
class FakeSessionService:
    def create_session(self, body):
        return SimpleNamespace(id=1, title=body.title, created_at=datetime.now())

    def update_session(self, id, body):
        return SimpleNamespace(id=id, title=body.title, created_at=datetime.now())

    def read_sessions(self, range_query):
        return []

    def read_single_session(self, id):
        return SimpleNamespace(id=id, title="Test Session")

    def delete_session(self, id):
        pass

@pytest.fixture(autouse=True)
def override_dependency():
    app.dependency_overrides[get_session_service] = lambda: FakeSessionService()
    yield
    app.dependency_overrides.clear()

def test_create_session(client):
    response = client.post("/sessions/", json={"title": "Session123"})
    assert response.status_code == 201
    assert response.json()["title"] == "Session123"


def test_list_sessions(client: TestClient):
    # 模擬的 service
    mock_service = MagicMock()
    mock_service.read_sessions.return_value = []  # 模擬返回空列表

    # 使用依賴注入覆寫
    app.dependency_overrides[get_session_service] = lambda: mock_service

    response = client.get("/sessions/")

    # 確保 status code 正常
    assert response.status_code == 200
    
    # 檢查返回是否為空
    data = response.json()
    assert isinstance(data, list)  # 確保返回類型為列表
    assert len(data) == 0  # 確保列表為空

    # 清除依賴覆蓋
    app.dependency_overrides.clear()


def test_get_session():
    response = client.get("/sessions/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Session"

def test_update_session(client):
    # 建立一筆測試資料
    create_response = client.post("/sessions/", json={"title": "ToUpdate"})
    session_id = create_response.json()["id"]

    # 測試更新
    update_response = client.put(f"/sessions/{session_id}", json={"title": "Updated123"})
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated123"


def test_delete_session():
    response = client.delete("/sessions/1")
    assert response.status_code == 204
