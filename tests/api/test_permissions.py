from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from tests.conftest import override_dependency, fake_current_admin_unauthenticated
from src.utils.auth import get_current_admin
import uuid


# ── success ──────────────────────────────────────────────────────────────────

@patch("src.models.permission.get_all_permissions")
def test_get_permissions_success(mock_get_all, client: TestClient):
    fake_permission_id = uuid.uuid4()

    mock_get_all.return_value = {
        "page": 1,
        "size": 10,
        "total": 2,
        "data": [
            {"id": str(fake_permission_id), "action": "view_posts", "resource":"admin","description": "Can view posts"},
            {"id": str(uuid.uuid4()), "action": "view_posts", "resource":"admin", "description": "Can edit posts"},
        ]
    }

    response = client.get("/permissions")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 2
    assert len(data["data"]) == 2
    assert data["data"][0]["id"] == str(fake_permission_id)
    mock_get_all.assert_called_once()


@patch("src.models.permission.get_all_permissions")
def test_get_permissions_empty(mock_get_all, client: TestClient):
    mock_get_all.return_value = {
        "page": 1,
        "size": 10,
        "total": 0,
        "data": []
    }

    response = client.get("/permissions")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["data"] == []


# ── pagination ────────────────────────────────────────────────────────────────

@patch("src.models.permission.get_all_permissions")
def test_get_permissions_pagination(mock_get_all, client: TestClient):
    mock_get_all.return_value = {
        "page": 2,
        "size": 5,
        "total": 12,
        "data": [{"id": str(uuid.uuid4()),  "action": "view_posts", "resource":"admin", "description": ""} for i in range(5)]
    }

    response = client.get("/permissions?page=2&size=5")

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["size"] == 5
    assert len(data["data"]) == 5


# ── unauthenticated ───────────────────────────────────────────────────────────

def test_get_permissions_unauthenticated(client: TestClient):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        response = client.get("/permissions")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"