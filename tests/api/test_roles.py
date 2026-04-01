import uuid

from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime
from src.models.role import Role

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