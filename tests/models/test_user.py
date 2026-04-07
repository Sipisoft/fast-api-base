import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from src.models.users import (
    User, UserRequest, UserPasswordResetRequest,
    create, update_user, user_actions, delete, get, get_all,
    set_new_password
)
from src.utils.models import Pagination
from src.utils.hash import Hash

@pytest.fixture
def current_user(db_session):
    user = User(
        username=f"current_user_{uuid4()}",
        email=f"current_{uuid4()}@example.com",
        name="Current User",
        password=Hash.encrypt("password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.mark.anyio
async def test_create_user_success(db_session, current_user):
    user_data = UserRequest(
        username=f"new_user_{uuid4()}",
        email=f"new_{uuid4()}@example.com",
        name="New User"
    )
    
    with patch("src.mailers.password_reset_mailer.PasswordResetMailer.send", return_value=None) as mock_send:
        mock_request = MagicMock()
        db_user = await create(db_session, user_data, current_user, request=mock_request)
        
        assert db_user.username == user_data.username
        assert db_user.email == user_data.email
        assert db_user.password_reset_token is not None
        mock_send.assert_called_once()

@pytest.mark.anyio
async def test_create_user_failure(db_session, current_user):
    user_data = UserRequest(
        username=f"another_user_{uuid4()}",
        email=current_user.email,
        name="Another User"
    )
    
    with pytest.raises(HTTPException) as exc:
        await create(db_session, user_data, current_user)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to create user" in exc.value.detail

def test_update_user_success(db_session, current_user):
    user_to_update = User(
        username=f"to_update_{uuid4()}",
        email=f"to_update_{uuid4()}@example.com",
        name="To Update"
    )
    db_session.add(user_to_update)
    db_session.commit()
    db_session.refresh(user_to_update)
    
    update_data = UserRequest(
        username=f"updated_user_{uuid4()}",
        email=f"updated_{uuid4()}@example.com",
        name="Updated User"
    )
    
    updated_user = update_user(db_session, user_to_update.id, update_data, current_user)
    
    assert updated_user.username == update_data.username
    assert updated_user.name == "Updated User"

def test_update_user_not_found(db_session, current_user):
    update_data = UserRequest(
        username=f"ghost_{uuid4()}",
        email=f"ghost_{uuid4()}@example.com",
        name="Ghost"
    )
    
    with pytest.raises(HTTPException) as exc:
        update_user(db_session, uuid4(), update_data, current_user)
    
    assert exc.value.status_code == 404

@pytest.mark.anyio
async def test_user_actions_deactivate(db_session, current_user):
    user = User(
        username=f"active_user_{uuid4()}",
        email=f"active_{uuid4()}@example.com",
        name="Active User",
        active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    result = await user_actions(db_session, user.id, current_user, "deactivate", MagicMock())
    assert result.active is False

@pytest.mark.anyio
async def test_user_actions_activate(db_session, current_user):
    user = User(
        username=f"inactive_user_{uuid4()}",
        email=f"inactive_{uuid4()}@example.com",
        name="Inactive User",
        active=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    result = await user_actions(db_session, user.id, current_user, "activate", MagicMock())
    assert result.active is True

@pytest.mark.anyio
async def test_user_actions_reset_password(db_session, current_user):
    user = User(
        username=f"reset_user_{uuid4()}",
        email=f"reset_{uuid4()}@example.com",
        name="Reset User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    with patch("src.mailers.password_reset_mailer.PasswordResetMailer.send", return_value=None) as mock_send:
        result = await user_actions(db_session, user.id, current_user, "reset_password", MagicMock())
        assert result.password_reset_token is not None
        mock_send.assert_called_once()

def test_delete_user_success(db_session, current_user):
    user = User(
        username=f"to_delete_{uuid4()}",
        email=f"delete_{uuid4()}@example.com",
        name="To Delete"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    delete(db_session, user.id, current_user)
    
    deleted_user = db_session.query(User).filter(User.id == user.id).first()
    assert deleted_user is None

def test_get_user_success(db_session, current_user):
    user = User(
        username=f"get_me_{uuid4()}",
        email=f"getme_{uuid4()}@example.com",
        name="Get Me"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    retrieved = get(db_session, user.id, current_user)
    assert retrieved.username == user.username

def test_get_all_users(db_session, current_user):
    pagination = Pagination(page=1, size=100, all=True)
    response = get_all(db_session, current_user, pagination)
    assert response.total >= 1
    # Check for presence in data, considering UserResponse model
    usernames = [a.username for a in response.data]
    assert current_user.username in usernames

def test_set_new_password_success(db_session):
    token = Hash.generate_token()
    user = User(
        username=f"pwd_reset_{uuid4()}",
        email=f"pwd_reset_{uuid4()}@example.com",
        name="Pwd Reset",
        password_reset_token=token,
        password_reset_token_expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    reset_data = UserPasswordResetRequest(
        password="newpassword123",
        password_confirmation="newpassword123",
        password_token=token
    )
    
    updated_user = set_new_password(db_session, reset_data)
    assert Hash.verify("newpassword123", updated_user.password)

def test_set_new_password_mismatch(db_session):
    reset_data = UserPasswordResetRequest(
        password="newpassword123",
        password_confirmation="different",
        password_token="some_token"
    )
    
    with pytest.raises(HTTPException) as exc:
        set_new_password(db_session, reset_data)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
