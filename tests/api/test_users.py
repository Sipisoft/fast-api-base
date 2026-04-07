from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from src.utils.auth import get_current_user
from tests.conftest import override_dependency

import uuid
from unittest.mock import patch, AsyncMock

def fake_current_user_unauthenticated():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def fake_user_response():
    id = uuid.uuid4()
    return {
        "id": id,
        "username": "testuser",
        "email": "testuser@test.com",
        "name": "Test User",
        "active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }



@patch("src.api.users.get_all")
def test_index_success(mock_get_all, client: TestClient):
    mock_get_all.return_value = {
        "page": 1,
        "size": 10,
        "total": 1,
        "data": [fake_user_response()],
        "start_date": None,
        "end_date": None,
        "total_pages": 1
    }

    response = client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["username"] == "testuser"
    assert data["data"][0]["name"] == "Test User"
    mock_get_all.assert_called_once()


@patch("src.api.users.get_all")
def test_index_empty(mock_get_all, client: TestClient):
    mock_get_all.return_value = {
        "page": 1,
        "size": 10,
        "total": 0,
        "data": [],
        "start_date": None,
        "end_date": None,
        "total_pages": 0
    }

    response = client.get("/users")

    assert response.status_code == 200
    assert response.json()["data"] == []


def test_index_unauthenticated(client: TestClient):
    with override_dependency(get_current_user, fake_current_user_unauthenticated):
        response = client.get("/users")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"



@patch("src.api.users.get_user")
def test_get_user_success(mock_get_user, client: TestClient):
    user = fake_user_response()
    mock_get_user.return_value = user

    response = client.get(f"/users/{user.get("id")}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.get("id"))
    assert data["username"] == "testuser"
    assert data["name"] == "Test User"
    assert data["email"] == "testuser@test.com"
    assert data["active"] is True
    assert "created_at" in data
    assert "updated_at" in data
    mock_get_user.assert_called_once()


@patch("src.api.users.get_user")
def test_get_user_not_found(mock_get_user, client: TestClient):
    mock_get_user.side_effect = HTTPException(status_code=404, detail="User not found")
    id = uuid.uuid4()
    response = client.get(f"/users/{id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_get_user_unauthenticated(client: TestClient):
    with override_dependency(get_current_user, fake_current_user_unauthenticated):
        id = uuid.uuid4()
        response = client.get(f"/users/{id}")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"



@patch("src.api.users.update_user")
def test_update_user_success(mock_update_user, client: TestClient):
    user_id = uuid.uuid4()
    mock_update_user.return_value = {**fake_user_response(), "username": "updateduser"}

    payload = {
        "username": "updateduser",
        "email": "testuser@test.com",
        "name": "Test User",
        "active": True,
    }

    response = client.put(f"/users/{user_id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updateduser"
    assert data["name"] == "Test User"
    mock_update_user.assert_called_once()


@patch("src.api.users.update_user")
def test_update_user_not_found(mock_update_user, client: TestClient):
    mock_update_user.side_effect = HTTPException(status_code=404, detail="User not found")
    id = uuid.uuid4()
    payload = {
        "username": "updateduser",
        "email": "testuser@test.com",
        "name": "Test User",
        "active": True,
    }
    response = client.put(f"/users/{id}", json = payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@patch("src.api.users.update_user")
def test_update_user_forbidden(mock_update_user, client: TestClient):
    mock_update_user.side_effect = HTTPException(status_code=403, detail="Not authorized to update this user")
    id = uuid.uuid4()
    payload = {
        "username": "updateduser",
        "email": "testuser@test.com",
        "name": "Test User",
        "active": True,
    }
    response = client.put(f"/users/{id}", json=payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to update this user"


def test_update_user_unauthenticated(client: TestClient):
    with override_dependency(get_current_user, fake_current_user_unauthenticated):
        id = uuid.uuid4()
        response = client.put(f"/users/{id}" ,json={"username": "x", "email": "x@x.com", "name": "X", "active": True})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"




@patch("src.api.users.user_actions", new_callable=AsyncMock)
def test_user_action_activate(mock_user_actions, client: TestClient):
    mock_user_actions.return_value = fake_user_response()

    response = client.put(f"/users/{uuid.uuid4()}/activate")

    assert response.status_code == 200
    assert response.json()["active"] is True
    mock_user_actions.assert_called_once()


@patch("src.api.users.user_actions", new_callable=AsyncMock)
def test_user_action_activate_not_found(mock_user_actions, client: TestClient):
    mock_user_actions.side_effect = HTTPException(status_code=404, detail="User not found")
    id = uuid.uuid4()
    action = "activate"
    response = client.put(f"/users/{id}/{action}")
    print(response.json())
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"



@patch("src.api.users.user_actions", new_callable=AsyncMock)
def test_user_action_deactivate(mock_actions, client: TestClient):
    user_id = uuid.uuid4()
    action ="deactivate"
    mock_actions.return_value = {**fake_user_response(), "active": False}

    response = client.put(f"/users/{user_id}/{action}")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["active"] is False
    mock_actions.assert_called_once()


@patch("src.api.users.user_actions", new_callable=AsyncMock)
def test_user_action_deactivate_not_found(mock_actions, client: TestClient):
    mock_actions.side_effect = HTTPException(status_code=404, detail="User not found")
    id = uuid.uuid4()
    action = "deactivate"
    response = client.put(f"/users/{id}/{action}")
    print(response.json())
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_user_action_unauthenticated(client: TestClient):
    with override_dependency(get_current_user, fake_current_user_unauthenticated):
        id = uuid.uuid4()
        action = "activate"
        response = client.put(f"/users/{id}/{action}")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"