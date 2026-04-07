from unittest.mock import patch
import uuid

from fastapi import HTTPException
from fastapi.testclient import TestClient
from tests.conftest import override_dependency,fake_current_admin_unauthenticated
from src.utils.auth import get_current_admin

def test_profile_index(client:TestClient):
    response = client.get("/profile")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@test.com"
    assert data["active"] == True

@patch("src.api.profile.update_admin")
def test_profile_update(mock_update_admin,client:TestClient):

    mock_update_admin.return_value = {
        "id":uuid.uuid4(),
        "email":"test@test.com",
        "role_id":uuid.uuid4(),
        "username":"testuser",
        "name":"newusername",
        "active":True,
        "created_at":"2023-01-01T00:00:00Z",
        "updated_at":"2023-01-01T00:00:00Z",
    }


    response = client.put("/profile",json={"name":"newusername","phone":"0123456789"})
    assert response.status_code == 201
    assert response.json()["name"] == "newusername"


@patch("src.api.profile.update_admin")
def test_profile_update_not_found(mock_update_admin,client:TestClient):
    mock_update_admin.side_effect = HTTPException(status_code=404, detail="Admin not found")

    response = client.put("/profile",json={"name":"newusername","phone":"0123456789"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Admin not found"


def test_profile_update_invalid_data(client:TestClient):
    response = client.put("/profile",json={"name":""})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["msg"] == "String should have at least 3 characters"

def test_profile_update_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        response = client.put("/profile",json={"name":"newusername","phone":"0123456789"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

def test_profile_index_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        response = client.get("/profile")

        assert response.status_code == 401


