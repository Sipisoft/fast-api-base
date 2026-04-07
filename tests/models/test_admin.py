import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from src.models.admin import (
    Admin, AdminRequest, AdminType, AdminPasswordResetRequest,
    create, update, admin_actions, delete, get, get_all,
    set_new_password, get_admin_by_email
)
from src.models.role import Role
from src.utils.models import Pagination
from src.utils.hash import Hash

@pytest.fixture
def sample_role(db_session):
    role = Role(id=uuid4(), name=f"Test Role {uuid4()}", description="Test Role Description")
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role

@pytest.fixture
def current_admin(db_session, sample_role):
    admin = Admin(
        username=f"current_admin_{uuid4()}",
        email=f"current_{uuid4()}@example.com",
        name="Current Admin",
        type=AdminType.internal,
        role_id=sample_role.id,
        password=Hash.encrypt("password123")
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

def test_create_admin_success(db_session, current_admin, sample_role):
    admin_data = AdminRequest(
        username=f"new_admin_{uuid4()}",
        email=f"new_{uuid4()}@example.com",
        name="New Admin",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    
    with patch("src.models.admin.trigger_password_reset_email") as mock_email:
        mock_request = MagicMock()
        db_admin = create(db_session, admin_data, current_admin, request=mock_request)
        
        assert db_admin.username == admin_data.username
        assert db_admin.email == admin_data.email
        assert db_admin.type == AdminType.internal
        assert db_admin.role_id == sample_role.id
        assert db_admin.password_reset_token is not None
        mock_email.assert_called_once()

def test_create_admin_failure(db_session, current_admin, sample_role):
    admin_data = AdminRequest(
        username=f"another_admin_{uuid4()}",
        email=current_admin.email, # Duplicate email
        name="Another Admin",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    
    with pytest.raises(HTTPException) as exc:
        create(db_session, admin_data, current_admin)
    
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "Failed to create admin" in exc.value.detail

def test_update_admin_success(db_session, current_admin, sample_role):
    admin_to_update = Admin(
        username=f"to_update_{uuid4()}",
        email=f"to_update_{uuid4()}@example.com",
        name="To Update",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    db_session.add(admin_to_update)
    db_session.commit()
    db_session.refresh(admin_to_update)
    
    update_data = AdminRequest(
        username=f"updated_admin_{uuid4()}",
        email=f"updated_{uuid4()}@example.com",
        name="Updated Admin",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    
    updated_admin = update(db_session, admin_to_update.id, update_data, current_admin)
    
    assert updated_admin.username == update_data.username
    assert updated_admin.name == "Updated Admin"

def test_update_admin_not_found(db_session, current_admin, sample_role):
    update_data = AdminRequest(
        username=f"ghost_{uuid4()}",
        email=f"ghost_{uuid4()}@example.com",
        name="Ghost",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    
    with pytest.raises(HTTPException) as exc:
        update(db_session, uuid4(), update_data, current_admin)
    
    assert exc.value.status_code == 404

def test_admin_actions_deactivate(db_session, current_admin, sample_role):
    admin = Admin(
        username=f"active_user_{uuid4()}",
        email=f"active_{uuid4()}@example.com",
        name="Active User",
        type=AdminType.internal,
        active=True,
        role_id=sample_role.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    result = admin_actions(db_session, admin.id, current_admin, "deactivate", MagicMock())
    assert result.active is False

def test_admin_actions_activate(db_session, current_admin, sample_role):
    admin = Admin(
        username=f"inactive_user_{uuid4()}",
        email=f"inactive_{uuid4()}@example.com",
        name="Inactive User",
        type=AdminType.internal,
        active=False,
        role_id=sample_role.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    result = admin_actions(db_session, admin.id, current_admin, "activate", MagicMock())
    assert result.active is True

def test_admin_actions_reset_password(db_session, current_admin, sample_role):
    admin = Admin(
        username=f"reset_user_{uuid4()}",
        email=f"reset_{uuid4()}@example.com",
        name="Reset User",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    with patch("src.models.admin.trigger_password_reset_email") as mock_email:
        result = admin_actions(db_session, admin.id, current_admin, "reset_password", MagicMock())
        assert result.password_reset_token is not None
        mock_email.assert_called_once()

def test_delete_admin_success(db_session, current_admin, sample_role):
    admin = Admin(
        username=f"to_delete_{uuid4()}",
        email=f"delete_{uuid4()}@example.com",
        name="To Delete",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    delete(db_session, admin.id, current_admin)
    
    deleted_admin = db_session.query(Admin).filter(Admin.id == admin.id).first()
    assert deleted_admin is None

def test_get_admin_success(db_session, current_admin, sample_role):
    admin = Admin(
        username=f"get_me_{uuid4()}",
        email=f"getme_{uuid4()}@example.com",
        name="Get Me",
        type=AdminType.internal,
        role_id=sample_role.id
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    retrieved = get(db_session, admin.id, current_admin)
    assert retrieved.username == admin.username

def test_get_all_admins(db_session, current_admin):
    pagination = Pagination(page=1, size=100, all=True) # Use all=True to bypass date filtering
    response = get_all(db_session, current_admin, pagination)
    assert response.total >= 1
    # Check for presence in data, considering AdminResponse model
    usernames = [a.username for a in response.data]
    assert current_admin.username in usernames

def test_set_new_password_success(db_session, sample_role):
    token = Hash.generate_token()
    admin = Admin(
        username=f"pwd_reset_{uuid4()}",
        email=f"pwd_reset_{uuid4()}@example.com",
        name="Pwd Reset",
        type=AdminType.internal,
        role_id=sample_role.id,
        password_reset_token=token,
        password_reset_token_expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    reset_data = AdminPasswordResetRequest(
        password="newpassword123",
        password_confirmation="newpassword123",
        password_token=token
    )
    
    updated_admin = set_new_password(db_session, reset_data)
    assert Hash.verify("newpassword123", updated_admin.password)

def test_set_new_password_mismatch(db_session):
    reset_data = AdminPasswordResetRequest(
        password="newpassword123",
        password_confirmation="different",
        password_token="some_token"
    )
    
    with pytest.raises(HTTPException) as exc:
        set_new_password(db_session, reset_data)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

def test_get_admin_by_email_success(db_session, current_admin):
    retrieved = get_admin_by_email(db_session, current_admin.email)
    assert retrieved.id == current_admin.id

def test_get_admin_by_email_not_found(db_session):
    with pytest.raises(HTTPException) as exc:
        get_admin_by_email(db_session, f"nonexistent_{uuid4()}@example.com")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
