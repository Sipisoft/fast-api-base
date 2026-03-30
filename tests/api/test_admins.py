import uuid
from fastapi import status,HTTPException
from fastapi.testclient import TestClient
from main import app
from src.utils.auth import get_current_admin

from unittest.mock import patch
from tests.conftest import override_dependency,fake_current_admin_unauthenticated
@patch("src.api.admins.get_admin")
def test_show_admin(mock_admin, client):
    test_id = uuid.uuid4()

    mock_admin.return_value = {
        "id": test_id,
        "email": "test@test.com",
        "role_id": uuid.uuid4(),
        "username": "testuser",
        "name": "Test User",
        "active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }

    response = client.get(f"/admins/{test_id}")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == str(test_id)
    assert data["email"] == "test@test.com"


def test_get_admin_not_found(client):
    test_id = uuid.uuid4()
    response = client.get(f"/admins/{test_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Admin not found"}

@patch("src.api.admins.get_all_admin")
def test_index(mock_get_all_admin,client):
    test_id = uuid.uuid4()
    fake_admins = [{
        "id": str(test_id),
        "email": "test@test.com",
        "role_id": str(test_id),
        "username": "testuser",
        "name": "Test User",
        "active": True,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
    }]

    mock_get_all_admin.return_value = {
        "page": 1,
        "size": 10,
        "data": fake_admins,
        "total": 1,
        "start_date": None,
        "end_date": None
    }

    response = client.get("/admins")
    assert response.status_code == 200
    data = response.json()

    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 1
    assert data["data"][0]["id"] == str(test_id)
    assert data["data"][0]["email"] == "test@test.com"

@patch("src.api.admins.create_admin")
def test_create_admin_success(mock_create_admin,client):
    test_id = uuid.uuid4()
    request_payload = {
        "username": "newadmin",
        "email": "newadmin@test.com",
        "role_id": str(uuid.uuid4()),
        "name": "New Admin",
        "active": True
    }

    mock_create_admin.return_value = {
        "id": str(test_id),
        **request_payload,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
    }

    response = client.post("/admins", json=request_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(test_id)
    assert data["username"] == "newadmin"
    assert data["email"] == "newadmin@test.com"

@patch("src.api.admins.update_admin")
def test_update_admin_success(mock_update_admin,client):
    admin_id = uuid.uuid4()
    request_payload = {
        "username": "updatedadmin",
        "email": "updated@test.com",
        "role_id": str(uuid.uuid4()),
        "name": "Updated Admin",
        "active": True
    }

    mock_update_admin.return_value = {
        "id": str(admin_id),
        **request_payload,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-03-01T00:00:00Z"
    }

    response = client.put(f"/admins/{admin_id}", json=request_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(admin_id)
    assert data["username"] == "updatedadmin"
    assert data["email"] == "updated@test.com"

@patch("src.api.admins.update_admin")
def test_update_admin_not_found(mock_update_admin,client):
    mock_update_admin.side_effect = HTTPException(status_code=404, detail="Admin not found")

    request_payload = {
        "username": "updatedadmin",
        "email": "updated@test.com",
        "role_id": str(uuid.uuid4()),
        "name": "Updated Admin",
        "active": True
    }

    admin_id = uuid.uuid4()
    response = client.put(f"/admins/{admin_id}", json=request_payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Admin not found"


# def test_index_unauthenticated(client):
#     with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
#
#         response = client.get("/admins")
#         assert response.status_code == 401
#         assert response.json()["detail"] == "Not authenticated"
#
#
# def test_show_unauthenticated(client):
#     with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
#         test_id = uuid.uuid4()
#         response = client.get(f"/admins/{test_id}")
#         assert response.status_code == 401
#         assert response.json()["detail"] == "Not authenticated"


# def test_create_admin_unauthenticated(client):
#     with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
#         request_payload = {
#             "username": "newadmin",
#             "email": "newadmin@test.com",
#             "role_id": str(uuid.uuid4()),
#             "name": "New Admin",
#             "active": True
#         }
#
#         response = client.post("/admins", json=request_payload)
#         assert response.status_code == 401
#         assert response.json()["detail"] == "Not authenticated"


# def test_update_admin_unauthenticated(client):
#     with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
#         request_payload = {
#             "username": "updatedadmin",
#             "email": "updated@test.com",
#             "role_id": str(uuid.uuid4()),
#             "name": "Updated Admin",
#             "active": True
#         }
#
#         admin_id = uuid.uuid4()
#         response = client.put(f"/admins/{admin_id}", json=request_payload)
#
#         assert response.status_code == 401
#         assert response.json()["detail"] == "Not authenticated"
#
