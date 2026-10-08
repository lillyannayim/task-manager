import copy

import pytest

from services.users import USERS, get_notification_pref, update_notification_pref
from utils.errors import NotFoundError, ValidationError


@pytest.fixture(autouse=True)
def restore_users():
    saved = copy.deepcopy(USERS)
    yield
    USERS.clear()
    USERS.update(saved)

@pytest.fixture
def client():
    from app import app
    return app.test_client()

@pytest.mark.parametrize("user_id", [1, 2])
def test_seed_users_default_notification_pref(user_id):
    assert get_notification_pref(user_id) == "none"

@pytest.mark.parametrize("pref", ["email", "sms", "none"])
def test_update_notification_pref_valid(pref):
    assert update_notification_pref(1, pref) == pref
    assert get_notification_pref(1) == pref

def test_update_notification_pref_invalid():
    with pytest.raises(ValidationError):
        update_notification_pref(1, "pigeon")
    assert get_notification_pref(1) == "none"

def test_get_notification_pref_not_found():
    with pytest.raises(NotFoundError):
        get_notification_pref(999)

def test_update_notification_pref_not_found():
    with pytest.raises(NotFoundError):
        update_notification_pref(999, "email")

def test_get_notification_pref_route(client):
    response = client.get("/api/users/1/notifications")
    assert response.status_code == 200
    assert response.get_json() == {"notification_pref": "none"}

def test_get_notification_pref_route_not_found(client):
    response = client.get("/api/users/999/notifications")
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"

def test_patch_notification_pref_route(client):
    response = client.patch("/api/users/2/notifications", json={"notification_pref": "sms"})
    assert response.status_code == 200
    assert response.get_json() == {"notification_pref": "sms"}
    assert client.get("/api/users/2/notifications").get_json()["notification_pref"] == "sms"

def test_patch_notification_pref_route_invalid(client):
    response = client.patch("/api/users/1/notifications", json={"notification_pref": "pigeon"})
    assert response.status_code == 422
    assert response.get_json()["error"].startswith("Invalid notification_pref")
    assert get_notification_pref(1) == "none"

def test_patch_notification_pref_route_not_found(client):
    response = client.patch("/api/users/999/notifications", json={"notification_pref": "email"})
    assert response.status_code == 404
    assert response.get_json()["error"] == "User not found"

def test_get_user_route_includes_notification_pref(client):
    response = client.get("/api/users/1")
    assert response.status_code == 200
    assert response.get_json()["notification_pref"] == "none"
