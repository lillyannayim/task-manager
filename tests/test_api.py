import pytest

from services.tasks import get_task


@pytest.fixture
def client():
    from app import app
    return app.test_client()

def test_post_task_route_with_priority(client):
    response = client.post("/api/tasks", json={"title": "Pay rent", "user_id": 1, "priority": 5})
    assert response.status_code == 201
    assert response.get_json()["priority"] == 5

def test_post_task_route_default_priority(client):
    response = client.post("/api/tasks", json={"title": "Read book", "user_id": 1})
    assert response.status_code == 201
    assert response.get_json()["priority"] == 3

def test_post_task_route_invalid_priority(client):
    response = client.post("/api/tasks", json={"title": "Bad", "user_id": 1, "priority": 9})
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Invalid priority")

def test_patch_task_route_priority(client):
    response = client.patch("/api/tasks/2", json={"priority": 1})
    assert response.status_code == 200
    assert response.get_json()["priority"] == 1
    assert response.get_json()["title"] == "Write report"

def test_patch_task_route_not_found(client):
    response = client.patch("/api/tasks/999", json={"priority": 2})
    assert response.status_code == 404

def test_patch_task_route_invalid_priority(client):
    response = client.patch("/api/tasks/2", json={"priority": 0})
    assert response.status_code == 422
    assert get_task(2)["priority"] == 3

def test_get_task_route_includes_priority(client):
    assert client.get("/api/tasks/1").get_json()["priority"] == 3

def test_get_tasks_route_all(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert {1, 2, 3} <= {task["id"] for task in response.get_json()}

def test_get_tasks_route_filter(client):
    client.patch("/api/tasks/2", json={"priority": 1})
    response = client.get("/api/tasks?priority=1")
    assert response.status_code == 200
    ids = {task["id"] for task in response.get_json()}
    assert 2 in ids
    assert not {1, 3} & ids

@pytest.mark.parametrize("priority", ["9", "abc"])
def test_get_tasks_route_invalid_priority(client, priority):
    response = client.get(f"/api/tasks?priority={priority}")
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Invalid priority")

def test_post_task_route_missing_title(client):
    response = client.post("/api/tasks", json={"user_id": 1})
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Invalid title")

def test_post_task_route_missing_user_id(client):
    response = client.post("/api/tasks", json={"title": "No owner"})
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Invalid user_id")

def test_post_task_route_user_not_found(client):
    response = client.post("/api/tasks", json={"title": "Ghost", "user_id": 999})
    assert response.status_code == 404
