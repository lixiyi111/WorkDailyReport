"""冒烟测试：确认应用可启动、健康检查可用。"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_ok() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"


def test_health_ok() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert set(body["credentials"]) == {"github", "feishu", "smtp"}
