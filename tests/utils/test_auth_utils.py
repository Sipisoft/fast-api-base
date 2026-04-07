import pytest
from datetime import timedelta, datetime, timezone
from jose import jwt
from fastapi import HTTPException, status
from unittest.mock import MagicMock, patch
from src.utils.auth import (
    create_access_token, SECRET_KEY, ALGORITHM,
    get_account, encode_basic_auth, generate_otp,
    generate_magic_link_token, verify_magic_link,
    verify_email_otp, send_otp_email
)
from src.models.admin import Admin, AdminType
from src.models.users import User
from src.models.otp_code import OtpCode, OtpPurpose
from src.utils.hash import Hash

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload

def test_create_access_token_custom_expiry():
    data = {"sub": "testuser"}
    expires = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=expires)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    # Allow some leeway for execution time
    assert exp > datetime.now(timezone.utc) + timedelta(minutes=9)
    assert exp < datetime.now(timezone.utc) + timedelta(minutes=11)

def test_get_account_success(db_session):
    admin = Admin(username="admin_auth", email="admin_auth@example.com", name="Admin Auth", active=True, type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    token = create_access_token({"sub": admin.username})
    
    result = get_account(Admin, token, db_session)
    assert result.id == admin.id
    assert result.username == admin.username

def test_get_account_invalid_token(db_session):
    with pytest.raises(HTTPException) as exc:
        get_account(Admin, "invalid_token", db_session)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_account_no_user(db_session):
    token = create_access_token({"sub": "non_existent"})
    with pytest.raises(HTTPException) as exc:
        get_account(Admin, token, db_session)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

def test_encode_basic_auth():
    encoded = encode_basic_auth("user", "pass")
    assert encoded.startswith("Basic ")
    # base64(user:pass) is dXNlcjpwYXNz
    assert encoded == "Basic dXNlcjpwYXNz"

def test_generate_otp():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()

def test_generate_magic_link_token():
    token = generate_magic_link_token()
    assert len(token) == 36  # UUID length

def test_verify_magic_link_success(db_session):
    admin = Admin(username="magic_admin", email="magic@example.com", name="Magic Admin", type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    token = "magic-token-123"
    otp_code = OtpCode(
        admin_id=admin.id,
        code="irrelevant",
        secret=token,
        purpose=OtpPurpose.LOGIN,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        active=True
    )
    db_session.add(otp_code)
    db_session.commit()
    
    result = verify_magic_link(token, db_session)
    assert result.id == admin.id
    assert otp_code.active is False
    assert otp_code.used_at is not None

def test_verify_magic_link_expired(db_session):
    admin = Admin(username="expired_admin", email="expired@example.com", name="Expired Admin", type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    token = "expired-token"
    otp_code = OtpCode(
        admin_id=admin.id,
        code="irrelevant",
        secret=token,
        purpose=OtpPurpose.LOGIN,
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        active=True
    )
    db_session.add(otp_code)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        verify_magic_link(token, db_session)
    assert exc.value.status_code == 400

def test_verify_email_otp_success(db_session):
    admin = Admin(username="otp_admin", email="otp@example.com", name="OTP Admin", type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    plain_otp = "123456"
    otp_code = OtpCode(
        admin_id=admin.id,
        code=Hash.encrypt(plain_otp),
        purpose=OtpPurpose.LOGIN,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        active=True
    )
    db_session.add(otp_code)
    db_session.commit()
    
    result = verify_email_otp(admin.email, plain_otp, db_session)
    assert result.id == admin.id
    assert otp_code.active is False

def test_verify_email_otp_invalid(db_session):
    admin = Admin(username="bad_otp_admin", email="bad_otp@example.com", name="Bad OTP Admin", type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    otp_code = OtpCode(
        admin_id=admin.id,
        code=Hash.encrypt("123456"),
        purpose=OtpPurpose.LOGIN,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
        active=True,
        attempts=0,
        max_attempts=3
    )
    db_session.add(otp_code)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        verify_email_otp(admin.email, "wrong", db_session)
    
    assert exc.value.status_code == 400
    assert otp_code.attempts == 1

@patch("src.utils.auth.send_otp_email_task.delay")
def test_send_otp_email_success(mock_delay, db_session):
    admin = Admin(username="send_otp", email="send_otp@example.com", name="Send OTP", type=AdminType.internal)
    db_session.add(admin)
    db_session.commit()
    
    send_otp_email(admin.email, db_session)
    
    mock_delay.assert_called_once()
    # Check if OtpCode was created
    otp = db_session.query(OtpCode).filter(OtpCode.admin_id == admin.id).first()
    assert otp is not None
    assert otp.purpose == OtpPurpose.LOGIN
