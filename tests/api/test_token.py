from fastapi.testclient import TestClient
from unittest.mock import patch
from src.models.admin import Admin
import uuid
from datetime import datetime


@patch("src.api.token.create_access_token")
@patch("src.api.token.Hash.verify")
def test_login_success(mock_verify, mock_create_token, client: TestClient, db_session):

    fake_user = Admin(
        id=uuid.uuid4(),
        username="admin",
        email="admin@test.com",
        password="hashedpassword",
        active=True,
        role_id=uuid.uuid4(),
        name="Admin User",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        type = "internal"
    )
    db_session.add(fake_user)
    db_session.commit()

    mock_verify.return_value = True
    mock_create_token.return_value = "fake-token"

    response = client.post(
        "/token",
        data={"username": "admin", "password": "password"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-token"
    assert response.json()["username"] == "admin"

    db_session.delete(fake_user)
    db_session.commit()


def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/token",
        data={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "User with username invalid not found"