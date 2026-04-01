import uuid
from unittest.mock import patch, MagicMock
from main import app
from src.db.database import get_db
from src.utils.auth import get_current_admin
from datetime import datetime
from tests.conftest import override_dependency,fake_current_admin_unauthenticated
from src.utils.auth import get_current_admin
from fastapi.testclient import TestClient

def test_list_api_keys(client):

    fake_response = {
        "page": 1,
        "size": 10,
        "total": 1,
        "data": [
            {
                "id": uuid.uuid4(),
                "name": "Test Key",
                "active": True,
                "created_at": str(datetime.now()),
                "description": "Test Description",
                "key_id":uuid.uuid4(),
                "secret": "test_secret_key",
                "callback_url": "https://example.com/callback",
                "admin_id": uuid.uuid4(),
            }
        ],
        "start_date": str(datetime.now()),
        "end_date": str(datetime.now())
    }

    with patch("src.api.api_keys.get_all", return_value=fake_response):

        response = client.get("/api-keys")

    assert response.status_code == 200
    assert response.json()["data"][0]["name"] == "Test Key"


@patch("src.api.api_keys.create")
def test_create_api_key(mock_create,client:TestClient):
    mock_create.return_value = {
        "id": uuid.uuid4(),
        "name": "Test Key",
        "active": True,
        "created_at": str(datetime.now()),
        "description": "Test Description",
        "key_id":uuid.uuid4(),
        "secret": "test_secret_key",
        "callback_url": "https://example.com/callback",
        "admin_id": uuid.uuid4(),
    }
    request_payload = {
                    "name":"Test Key",
                    "description": "Test Description",
                   "callback_url":"https://example.com/callback",
                    "callback_username":"testuser",
                    "callback_password":"testpassword"}
    response = client.post("/api-keys",json=request_payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Key"
    assert response.json()["description"] == "Test Description"
    assert response.json()["callback_url"] == "https://example.com/callback"


def test_list_api_keys_unauthenticated(client):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        response = client.get("/api-keys")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

def test_create_api_key_unauthenticated(client):
    with override_dependency(get_current_admin, fake_current_admin_unauthenticated):
        request_payload = {
            "name": "Test Key",
            "description": "Test Description",
            "callback_url": "https://example.com/callback",
            "callback_username": "testuser",
            "callback_password": "testpassword"
        }
        response = client.post("/api-keys", json=request_payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"


def test_create_api_key_invalid_data(client):
    request_payload = {
        "name": "",
        "description": "Test Description",
        "callback_url": "https://example.com/callback",
        "callback_username": "testuser",
        "callback_password": "testpassword"
    }
    response = client.post("/api-keys", json=request_payload)
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "String should have at least 3 characters"
