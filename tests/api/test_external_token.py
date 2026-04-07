from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from tests.conftest import override_dependency
from src.utils.auth import get_current_api_key
from src.models.api_client_token import ApiClientToken
from main import app
import uuid
from datetime import datetime, timezone


def make_fake_api_key():
    fake = MagicMock(spec=ApiClientToken, name="fake_api_key")
    fake.id = uuid.uuid4()
    fake.api_key_id = uuid.uuid4()
    fake.expires_at = datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc)
    fake.created_at = datetime.now()
    return fake


def fake_token_response():
    return {
        "token": str(uuid.uuid4()),
        "expires_at": datetime(2026, 5, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
    }


# ── success ──────────────────────────────────────────────────────────────────

@patch("src.api.external_token.create_api_token")
def test_create_token_success(mock_create, client: TestClient):
    fake_api_key = make_fake_api_key()
    expected = fake_token_response()
    mock_create.return_value = expected

    app.dependency_overrides[get_current_api_key] = lambda: fake_api_key
    try:
        response = client.post("/external-token")

    finally:
        app.dependency_overrides.pop(get_current_api_key, None)

    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "expires_at" in data
    mock_create.assert_called_once()


# ── unauthenticated ───────────────────────────────────────────────────────────

def test_create_token_missing_api_key(client: TestClient):
    def fake_missing():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    app.dependency_overrides[get_current_api_key] = fake_missing
    try:
        response = client.post("/external-token")
    finally:
        app.dependency_overrides.pop(get_current_api_key, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing API key"


def test_create_token_invalid_api_key(client: TestClient):
    def fake_invalid():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    app.dependency_overrides[get_current_api_key] = fake_invalid
    try:
        response = client.post("/external-token")
    finally:
        app.dependency_overrides.pop(get_current_api_key, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key"


def test_create_token_inactive_api_key(client: TestClient):
    def fake_inactive():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="API key is inactive")

    app.dependency_overrides[get_current_api_key] = fake_inactive
    try:
        response = client.post("/external-token")
    finally:
        app.dependency_overrides.pop(get_current_api_key, None)

    assert response.status_code == 403
    assert response.json()["detail"] == "API key is inactive"


# ── downstream failure ────────────────────────────────────────────────────────

@patch("src.api.external_token.create_api_token")
def test_create_token_db_failure(mock_create, client: TestClient):
    fake_api_key = make_fake_api_key()
    mock_create.side_effect = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Token creation failed"
    )

    app.dependency_overrides[get_current_api_key] = lambda: fake_api_key
    try:
        response = client.post("/external-token")
    finally:
        app.dependency_overrides.pop(get_current_api_key, None)

    assert response.status_code == 500
    assert response.json()["detail"] == "Token creation failed"