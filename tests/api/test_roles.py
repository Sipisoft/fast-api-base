import uuid

from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from src.models.role import Role
from tests.conftest import override_dependency,fake_current_admin_unauthenticated
from src.utils.auth import get_current_admin

@patch("src.api.roles.get_all")
def test_get_roles(mock_get_all,client:TestClient):
    fake_id = uuid.uuid4()
    fake_roles = {
        "id": fake_id,
        "name": "admin",
        "description": "Admin role",
        "active": True,
        "permissions":[]
    }
    mock_get_all.return_value ={
        "page": 1,
        "size": 10,
        "data": [fake_roles],
        "total": 1,
        "start_date": f"{datetime.today()}",
        "end_date": f"{datetime.today()}"
    }
    response = client.get("/roles")

    assert response.status_code == 200
    assert response.json()["page"] == 1
    assert response.json()["size"] == 10
    assert response.json()["total"] == 1
    assert response.json()["data"][0]["id"] == str(fake_id)

@patch("src.api.roles.get_one")
def test_role(mock_get_one,client:TestClient):
    fake_id = uuid.uuid4()
    fake_role = Role(
        id=fake_id,
        name="admin",
        description="Admin role",
        active=True,
        permissions=[]
    )
    mock_get_one.return_value = fake_role
    response = client.get(f"/roles/{fake_id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(fake_id)

def test_role_not_found(client:TestClient):
    fake_id = uuid.uuid4()
    response = client.get(f"/roles/{fake_id}")
    assert response.status_code == 404

def test_create_role(client:TestClient):
    request_payload = {
        "name": "newrole",
        "description": "New role",
        "permission_ids":[]
    }
    response = client.post("/roles",json=request_payload)
    assert response.status_code == 201
    assert response.json()["name"] == "newrole"

@patch("src.api.roles.update")
def test_update_role(mock_update,client:TestClient):
    fake_id = uuid.uuid4()
    request_payload = {
        "name": "updatedrole",
        "description": "Updated role",
        "permission_ids":[]
    }
    mock_update.return_value = {
        **request_payload,
        "id": fake_id,
        "active": True,
        "permissions": [],
    }

    response = client.put(f"/roles/{fake_id}",json=request_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "updatedrole"
    assert response.json()["description"] == "Updated role"

def test_update_role_not_found(client:TestClient):
    fake_id = uuid.uuid4()
    request_payload = {
        "name": "updatedrole",
        "description": "Updated role",
        "permission_ids":[]
    }
    response = client.put(f"/roles/{fake_id}",json=request_payload)
    assert response.status_code == 404

@patch("src.api.roles.role_actions")
def test_update_action(mock_role_actions,client:TestClient):
    fake_id = uuid.uuid4()
    fake_action = "deactivate"
    mock_role_actions.return_value = {
        "id": fake_id,
        "name": "admin",
        "description": "Admin role",
        "active": False,
        "permissions":[]
    }
    response = client.put(f"/roles/{fake_id}/{fake_action}")
    assert response.status_code == 200
    assert response.json()["active"] == False

def test_update_action_not_found(client:TestClient):
    fake_id = uuid.uuid4()
    fake_action = ""
    response = client.put(f"/roles/{fake_id}/{fake_action}")
    assert response.status_code == 404

@patch("src.api.roles.role_actions")
def test_update_action_bad_action(mock_role_actions,client:TestClient):
    fake_id = uuid.uuid4()
    fake_action = "badaction"
    mock_role_actions.side_effect = HTTPException(status_code=400, detail="Invalid action")
    response = client.put(f"/roles/{fake_id}/{fake_action}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid action"

def test_get_roles_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        response = client.get("/roles")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

def test_role_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        fake_id = uuid.uuid4()
        response = client.get(f"/roles/{fake_id}")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_create_role_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        request_payload = {
            "name": "newrole",
            "description": "New role",
            "permission_ids":[]
        }
        response = client.post("/roles",json=request_payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_update_role_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        fake_id = uuid.uuid4()
        request_payload = {
            "name": "updatedrole",
            "description": "Updated role",
            "permission_ids":[]
        }
        response = client.put(f"/roles/{fake_id}",json=request_payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_update_action_unauthenticated(client:TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        fake_id = uuid.uuid4()
        fake_action = "deactivate"
        response = client.put(f"/roles/{fake_id}/{fake_action}")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


