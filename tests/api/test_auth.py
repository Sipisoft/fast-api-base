from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@patch("src.api.auth.set_new_password")
def test_set_password_success(mock_set_new_password, client: TestClient):
    mock_set_new_password.return_value = None

    response = client.post("/auth/set-password", json={
        "password_token": "valid-reset-token",
        "password": "NewSecurePass123!",
        "password_confirmation": "NewSecurePass123!"

    })

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successfully!"}
    mock_set_new_password.assert_called_once()


@patch("src.api.auth.set_new_password")
def test_set_password_invalid_token(mock_set_new_password, client: TestClient):
    from fastapi import HTTPException
    mock_set_new_password.side_effect = HTTPException(status_code=400, detail="Invalid or expired token")

    response = client.post("/auth/set-password", json={
        "password_token": "bad-token",
        "password": "NewSecurePass123!",
        "password_confirmation": "NewSecurePass123!"
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"



@patch("src.api.auth.send_otp_email")
def test_send_otp_success(mock_send_otp_email, client: TestClient):
    mock_send_otp_email.return_value = None

    response = client.post("/auth/send-otp", json={"email": "admin@test.com"})

    assert response.status_code == 200
    assert response.json() == {"message": "OTP sent successfully!"}
    mock_send_otp_email.assert_called_once()


@patch("src.api.auth.send_otp_email")
def test_send_otp_email_not_found(mock_send_otp_email, client: TestClient):
    from fastapi import HTTPException
    mock_send_otp_email.side_effect = HTTPException(status_code=404, detail="Admin not found")

    response = client.post("/auth/send-otp", json={"email": "ghost@test.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Admin not found"


@patch("src.api.auth.send_otp_email")
def test_send_otp_inactive_account(mock_send_otp_email, client: TestClient):
    from fastapi import HTTPException
    mock_send_otp_email.side_effect = HTTPException(status_code=403, detail="Account is inactive")

    response = client.post("/auth/send-otp", json={"email": "inactive@test.com"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is inactive"



@patch("src.api.auth.create_access_token")
@patch("src.api.auth.verify_email_otp")
def test_verify_otp_success(mock_verify_otp, mock_create_token, client: TestClient):
    fake_admin = MagicMock()
    fake_admin.username = "adminuser"

    mock_verify_otp.return_value = fake_admin
    mock_create_token.return_value = "otp-access-token"

    response = client.post("/auth/verify-otp", json={
        "email": "admin@test.com",
        "otp": "123456"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "otp-access-token"
    assert data["token_type"] == "bearer"
    mock_create_token.assert_called_once_with({"sub": "adminuser"})


@patch("src.api.auth.verify_email_otp")
def test_verify_otp_invalid(mock_verify_otp, client: TestClient):
    from fastapi import HTTPException
    mock_verify_otp.side_effect = HTTPException(status_code=401, detail="Invalid or expired OTP")

    response = client.post("/auth/verify-otp", json={
        "email": "admin@test.com",
        "otp": "000000"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired OTP"


@patch("src.api.auth.verify_email_otp")
def test_verify_otp_expired(mock_verify_otp, client: TestClient):
    from fastapi import HTTPException
    mock_verify_otp.side_effect = HTTPException(status_code=410, detail="OTP has expired")

    response = client.post("/auth/verify-otp", json={
        "email": "admin@test.com",
        "otp": "123456"
    })

    assert response.status_code == 410
    assert response.json()["detail"] == "OTP has expired"



@patch("src.api.auth.create_access_token")
@patch("src.api.auth.verify_magic_link")
def test_verify_magic_link_success(mock_verify_magic_link, mock_create_token, client: TestClient):
    fake_admin = MagicMock()
    fake_admin.username = "adminuser"

    mock_verify_magic_link.return_value = fake_admin
    mock_create_token.return_value = "magic-access-token"

    response = client.get("/auth/magic-link", params={"token": "valid-magic-token"})

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "magic-access-token"
    assert data["token_type"] == "bearer"
    mock_create_token.assert_called_once_with({"sub": "adminuser"})


@patch("src.api.auth.verify_magic_link")
def test_verify_magic_link_invalid(mock_verify_magic_link, client: TestClient):
    from fastapi import HTTPException
    mock_verify_magic_link.side_effect = HTTPException(status_code=401, detail="Invalid magic link")

    response = client.get("/auth/magic-link", params={"token": "bad-token"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid magic link"


@patch("src.api.auth.verify_magic_link")
def test_verify_magic_link_expired(mock_verify_magic_link, client: TestClient):
    from fastapi import HTTPException
    mock_verify_magic_link.side_effect = HTTPException(status_code=410, detail="Magic link has expired")

    response = client.get("/auth/magic-link", params={"token": "expired-token"})

    assert response.status_code == 410
    assert response.json()["detail"] == "Magic link has expired"


@patch("src.api.auth.verify_magic_link")
def test_verify_magic_link_already_used(mock_verify_magic_link, client: TestClient):
    from fastapi import HTTPException
    mock_verify_magic_link.side_effect = HTTPException(status_code=409, detail="Magic link already used")

    response = client.get("/auth/magic-link", params={"token": "used-token"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Magic link already used"